"""Run bootstrap against an isolated fake SSH/Git service, never a real server."""
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
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
elif args[:2]==['rev-parse','FETCH_HEAD']: print('1'*40)
elif args[0]=='show' and args[1]=='1'*40+':deployment.json': print((root/'.git/deployment.json').read_text())
elif args[:3]==['remote','get-url','origin']: print((root/'.git/origin').read_text())
elif args[:3]==['remote','set-url','origin']: (root/'.git/origin').write_text(args[3])
elif args[0]=='status':
 if (root/'.git/dirty').exists(): print(' M keep-local')
elif args[0] not in ['config','fetch','pull','submodule']: raise SystemExit('unexpected git command')
'''
SSH = '''import json,os,shlex,subprocess,sys
command=sys.argv[-1]
env=dict(os.environ,HOME=os.environ['FAKE_REMOTE_HOME'])
with open(os.environ['FAKE_SSH_LOG'],'a') as f: f.write(json.dumps(command)+'\\n')
raise SystemExit(subprocess.run(shlex.split(command),env=env).returncode)
'''


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.root=work/uuid.uuid4().hex; self.root.mkdir(mode=0o700)
        self.home=self.root/'controller'; self.home.mkdir(mode=0o700)
        self.remote=self.root/'remote'; self.remote.mkdir(mode=0o700)
        self.bin=self.root/'bin'; self.bin.mkdir()
        self.config=write_snapshot(self.root)
        self.log=self.root/'git-log'
        self.ssh_log=self.root/'ssh-log'
        for name,source in [('git',GIT),('ssh',SSH)]:
            p=self.bin/name; p.write_text('#!'+sys.executable+'\n'+source); p.chmod(0o700)
        for name,body in [('uname','case \"$1\" in -m) echo x86_64;; *) echo Linux;; esac'),('age','echo age-test'),
                          ('age-keygen','echo age1synthetic'),('sha256sum','exit 0')]:
            p=self.bin/name; p.write_text('#!/bin/sh\n'+body+'\n'); p.chmod(0o700)
        fleet=self.home/'.config/agent-update/fleet'; fleet.mkdir(mode=0o700,parents=True)
        for name in ['fleet.agekey','private-repo-ed25519','private-repo-ed25519.pub','github_known_hosts']:
            p=fleet/name; p.write_text('synthetic fixture\n'); p.chmod(0o600)
        self.env=dict(os.environ,HOME=str(self.home),PATH=str(self.bin)+':'+os.environ['PATH'],
                      FAKE_REMOTE_HOME=str(self.remote),FAKE_GIT_LOG=str(self.log),
                      FAKE_SSH_LOG=str(self.ssh_log))
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

    def run_bootstrap(self, *, snapshot=True, profile='example-profile'):
        args = ['/bin/bash', str(script), 'synthetic-host']
        if profile is not None:
            args.append(profile)
        if snapshot:
            args += ['--deployment-config', str(self.config)]
        return subprocess.run(args, env=self.env, capture_output=True, text=True, timeout=30)

    def test_omitted_profile_and_snapshot_path_with_spaces(self):
        renamed = self.root / 'deployment settings.json'
        self.config.rename(renamed); self.config = renamed
        result = self.run_bootstrap(profile=None)
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = subprocess.check_output(['hostname', '-s'], text=True).strip()
        self.assertEqual(json.loads(self.registration.read_text())['profile'], expected)

    def test_default_configuration_from_registered_controller(self):
        checkout = self.home / '.config/agent-update/repository'
        checkout.mkdir(mode=0o700)
        metadata = checkout / '.git'; metadata.mkdir()
        (metadata / 'origin').write_text(CONFIG['bootstrap']['private_url'])
        (metadata / 'deployment.json').write_text(json.dumps(CONFIG))
        registration = self.home / '.config/agent-update/private-sync.json'
        registration.write_text(json.dumps({'checkout': str(checkout),
                                            'repository_url': CONFIG['bootstrap']['private_url']}))
        registration.chmod(0o600)
        result = self.run_bootstrap(snapshot=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = json.loads(self.registration.read_text())
        self.assertEqual(installed['repository_url'], CONFIG['bootstrap']['private_url'])
        self.assertEqual(installed['github_account'], CONFIG['bootstrap']['github_account'])

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
        packet = base64.b64encode(json.dumps(CONFIG, separators=(',', ':')).encode()).decode()
        self.assertNotIn(packet, self.ssh_log.read_text())

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

    def test_failed_verifier_install_can_be_retried_without_replacing_keys(self):
        result = self.run_bootstrap(); self.assertEqual(result.returncode, 0, result.stderr)
        key = self.remote / '.config/agent-update/fleet/fleet.agekey'
        before = key.read_bytes()
        keygen = self.bin / 'age-keygen'
        original = keygen.read_text()
        keygen.write_text('#!' + sys.executable + '\nimport os,sys\n'
                          "if os.environ['HOME'] == os.environ['FAKE_REMOTE_HOME']: raise SystemExit(127)\n"
                          + original.split('\n', 1)[1])
        source = self.root / 'age-source'; source.mkdir()
        (source / 'age').write_text('#!/bin/sh\necho age-test\n')
        (source / 'age-keygen').write_text(original)
        archive = self.root / 'age.tgz'
        with tarfile.open(archive, 'w:gz') as bundle:
            bundle.add(source, arcname='age')
        self.env['FAKE_AGE_ARCHIVE'] = str(archive)
        curl = self.bin / 'curl'; curl.write_text('#!/bin/sh\nexit 22\n'); curl.chmod(0o700)
        self.assertNotEqual(self.run_bootstrap().returncode, 0)
        self.assertEqual(key.read_bytes(), before)
        self.assertFalse((self.remote / '.local/state/agent-update/writer.lock').exists())
        self.assertFalse(list((self.remote / '.local/bin').glob('.age-install.*')))
        curl.write_text('#!' + sys.executable + '\nimport os,shutil,sys\n'
                        "shutil.copyfile(os.environ['FAKE_AGE_ARCHIVE'], sys.argv[sys.argv.index('-o') + 1])\n")
        result = self.run_bootstrap(); self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(key.read_bytes(), before)
        self.assertTrue((self.remote / '.local/bin/age-keygen').is_file())

    def test_invalid_settings_fail_before_ssh_or_key_transfer(self):
        config=json.loads(self.config.read_text()); config['bootstrap']['private_url']='$(touch bad)'
        self.config.write_text(json.dumps(config))
        self.assertNotEqual(self.run_bootstrap().returncode,0)
        self.assertEqual(list(self.remote.iterdir()),[])
        self.assertFalse(self.log.exists())


unittest.main()
