"""Run bootstrap against an isolated fake SSH/Git service, never a real server."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import uuid
from test_deployment_config import CONFIG, write_snapshot

script = Path(__file__).with_name('bootstrap-remote').resolve()
work = Path(sys.argv.pop(1)).resolve(); work.mkdir(mode=0o700, parents=True, exist_ok=True)

GIT = '''import json,os,pathlib,sys
args=sys.argv[1:]
with open(os.environ['FAKE_GIT_LOG'],'a') as f: f.write(json.dumps(args)+'\\n')
root=None
if args[:1]==['-C']: root=pathlib.Path(args[1]); args=args[2:]
if args[0]=='clone':
 root=pathlib.Path(args[-1]); root.mkdir(parents=True); (root/'.git').mkdir()
 (root/'.git/origin').write_text(args[-2])
elif args[:2]==['rev-parse','--show-toplevel']: print(root.resolve())
elif args[:3]==['remote','get-url','origin']: print((root/'.git/origin').read_text())
elif args[:3]==['remote','set-url','origin']: (root/'.git/origin').write_text(args[3])
elif args[0]=='status':
 if (root/'.git/dirty').exists(): print(' M keep-local')
elif args[0] not in ['config','fetch','pull','submodule']: raise SystemExit('unexpected git command')
'''
SSH = '''import os,subprocess,sys
command=sys.argv[-1]
env=dict(os.environ,HOME=os.environ['FAKE_REMOTE_HOME'])
raise SystemExit(subprocess.run(['/bin/bash','-c',command],env=env).returncode)
'''


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.root=work/uuid.uuid4().hex; self.root.mkdir(mode=0o700)
        self.home=self.root/'controller'; self.home.mkdir(mode=0o700)
        self.remote=self.root/'remote'; self.remote.mkdir(mode=0o700)
        self.bin=self.root/'bin'; self.bin.mkdir()
        self.config=write_snapshot(self.root)
        self.log=self.root/'git-log'
        for name,source in [('git',GIT),('ssh',SSH)]:
            p=self.bin/name; p.write_text('#!'+sys.executable+'\n'+source); p.chmod(0o700)
        for name,body in [('uname','echo Linux'),('age','echo age-test'),
                          ('age-keygen','echo age1synthetic'),('sha256sum','exit 0')]:
            p=self.bin/name; p.write_text('#!/bin/sh\n'+body+'\n'); p.chmod(0o700)
        fleet=self.home/'.config/agent-update/fleet'; fleet.mkdir(mode=0o700,parents=True)
        for name in ['fleet.agekey','private-repo-ed25519','private-repo-ed25519.pub','github_known_hosts']:
            p=fleet/name; p.write_text('synthetic fixture\n'); p.chmod(0o600)
        self.env=dict(os.environ,HOME=str(self.home),PATH=str(self.bin)+':'+os.environ['PATH'],
                      FAKE_REMOTE_HOME=str(self.remote),FAKE_GIT_LOG=str(self.log))
        self.env.pop('XDG_STATE_HOME',None)
        keygen=self.bin/'age-keygen'
        keygen.write_text('#!'+sys.executable+'\n'+
            "import os,pathlib,sys\nroot=pathlib.Path(os.environ['FAKE_REMOTE_HOME'])\n"+
            "if str(sys.argv[-1]).startswith(str(root)):\n"+
            " assert (root/'.local/state/agent-update/writer.lock').is_dir(), 'identity check outside lock'\n"+
            "print('age1other' if (root/'reject-key').exists() and str(sys.argv[-1]).startswith(str(root)) else 'age1synthetic')\n")
        keygen.chmod(0o700)
        self.registration=self.remote/'.config/agent-update/private-sync.json'

    def tearDown(self):
        assert self.root.parent==work and not self.root.is_symlink()
        shutil.rmtree(self.root)

    def run_bootstrap(self):
        return subprocess.run(['/bin/bash',str(script),'synthetic-host','example-profile',
                               '--deployment-config',str(self.config)],env=self.env,
                              capture_output=True,text=True,timeout=30)

    def test_initial_install_and_repeat_preserve_account_and_layout(self):
        result=self.run_bootstrap(); self.assertEqual(result.returncode,0,result.stderr)
        reg=json.loads(self.registration.read_text())
        self.assertEqual(reg['repository_url'],CONFIG['bootstrap']['private_url'])
        self.assertEqual(reg['github_account'],CONFIG['bootstrap']['github_account'])
        self.assertEqual(reg['profile'],'example-profile')
        self.assertEqual((self.remote/'.config/agent-update/repository').stat().st_mode&0o777,0o700)
        self.assertEqual(self.registration.stat().st_mode&0o777,0o600)
        self.assertEqual((self.remote/'dotfiles/agent-file-sync.local.yaml').read_text(),'mode: host-global\n')
        reg['github_account']='retained-account'; self.registration.write_text(json.dumps(reg))
        result=self.run_bootstrap(); self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(self.registration.read_text())['github_account'],'retained-account')
        self.assertFalse((self.remote/'.local/state/agent-update/writer.lock').exists())
        calls=[json.loads(x) for x in self.log.read_text().splitlines()]
        self.assertTrue(any('pull' in c and '--ff-only' in c for c in calls))

    def test_wrong_origin_and_dirty_checkout_preserve_registration(self):
        result=self.run_bootstrap(); self.assertEqual(result.returncode,0,result.stderr)
        before=self.registration.read_bytes(); repo=self.remote/'dotfiles/.git'
        original=(repo/'origin').read_text(); (repo/'origin').write_text('https://github.com/other/repo.git')
        self.assertNotEqual(self.run_bootstrap().returncode,0)
        self.assertEqual(self.registration.read_bytes(),before)
        (repo/'origin').write_text(original); (repo/'dirty').write_text('keep')
        self.assertNotEqual(self.run_bootstrap().returncode,0)
        self.assertEqual(self.registration.read_bytes(),before)
        self.assertEqual((repo/'dirty').read_text(),'keep')

    def test_held_lock_and_identity_mismatch_preserve_existing_keys(self):
        result=self.run_bootstrap(); self.assertEqual(result.returncode,0,result.stderr)
        key=self.remote/'.config/agent-update/fleet/fleet.agekey'; before=key.read_bytes()
        lock=self.remote/'.local/state/agent-update/writer.lock'; lock.mkdir()
        self.assertNotEqual(self.run_bootstrap().returncode,0)
        self.assertEqual(key.read_bytes(),before); self.assertTrue(lock.exists())
        lock.rmdir(); (self.remote/'reject-key').write_text('reject')
        self.assertNotEqual(self.run_bootstrap().returncode,0)
        self.assertEqual(key.read_bytes(),before)
        self.assertFalse(lock.exists())

    def test_invalid_settings_fail_before_ssh_or_key_transfer(self):
        config=json.loads(self.config.read_text()); config['bootstrap']['private_url']='$(touch bad)'
        self.config.write_text(json.dumps(config))
        self.assertNotEqual(self.run_bootstrap().returncode,0)
        self.assertEqual(list(self.remote.iterdir()),[])
        self.assertFalse(self.log.exists())


unittest.main()
