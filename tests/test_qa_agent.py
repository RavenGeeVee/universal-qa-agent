import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "qa_agent.py"
SPEC = importlib.util.spec_from_file_location("qa_agent", SCRIPT)
qa_agent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qa_agent)
AGENT_INSTALLER_SPEC = importlib.util.spec_from_file_location("install_agent_skills", SCRIPT.parent / "install_agent_skills.py")
agent_installer = importlib.util.module_from_spec(AGENT_INSTALLER_SPEC)
AGENT_INSTALLER_SPEC.loader.exec_module(agent_installer)
PACKAGE_SCRIPT = SCRIPT.parent / "package_plugin.py"
PACKAGE_SPEC = importlib.util.spec_from_file_location("package_plugin", PACKAGE_SCRIPT)
packager = importlib.util.module_from_spec(PACKAGE_SPEC)
PACKAGE_SPEC.loader.exec_module(packager)


def approved_profile(repo, store):
    identity = qa_agent.repository_identity(repo)
    directory = store / f"repo-{identity['key'][7:]}"
    directory.mkdir(parents=True)
    profile = qa_agent.yaml.safe_load((SCRIPT.parents[1] / "repo-profiles/template/profile.yaml").read_text(encoding="utf-8"))
    profile["repository"].update(name=Path(repo).name, root=str(Path(repo)))
    profile["repository"]["identity"] = identity
    (directory / "profile.yaml").write_text(qa_agent.yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    (directory / "conventions.md").write_text("conventions", encoding="utf-8")
    (directory / "patterns.md").write_text("patterns", encoding="utf-8")
    files = qa_agent._profile_files(directory)
    marker = {"identity_key": identity["key"], "content_digest": qa_agent._content_digest(files)}
    (directory / qa_agent.APPROVAL_MARKER).write_text(json.dumps(marker), encoding="utf-8")
    return directory


class ProfileLoadingTests(unittest.TestCase):
    def test_default_store_is_outside_the_plugin(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary).resolve()
            with mock.patch.dict(os.environ, {"UQA_PROFILES_DIR": ""}), mock.patch.object(Path, "home", return_value=home):
                self.assertEqual(home / ".local/share/universal-qa-agent/repo-profiles", qa_agent.profiles_root())

    def test_environment_override_expands_home(self):
        with mock.patch.dict(os.environ, {"UQA_PROFILES_DIR": "~/qa-profiles"}):
            self.assertEqual((Path.home() / "qa-profiles").resolve(), qa_agent.profiles_root())

    def test_relative_environment_override_is_rejected(self):
        with mock.patch.dict(os.environ, {"UQA_PROFILES_DIR": "relative/profiles"}):
            with self.assertRaises(ValueError):
                qa_agent.profiles_root()

    def test_discovery_handles_first_use_and_excludes_drafts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "profiles"
            self.assertEqual([], qa_agent.available_profiles(root))
            accepted = Path(temporary) / "accepted"
            accepted.mkdir()
            approved = approved_profile(accepted, root)
            draft = root / ("repo-" + "0" * 64)
            draft.mkdir()
            (draft / "profile.yaml").write_text("draft", encoding="utf-8")
            self.assertEqual([approved], qa_agent.available_profiles(root))

    def test_loads_profile_knowledge_by_identity_key(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "DemoMobileAutomation"
            repository.mkdir()
            profile = approved_profile(repository, root / "profiles")

            loaded_dir, contents = qa_agent.load_profile(str(repository), root / "profiles")

            self.assertEqual(profile, loaded_dir)
            self.assertEqual(list(qa_agent.KNOWLEDGE_FILES), [name for name, _ in contents])

    def test_missing_profile_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "Unprofiled"
            repository.mkdir()

            with self.assertRaises(FileNotFoundError):
                qa_agent.load_profile(str(repository), root / "profiles")

    def test_default_loading_and_discovery_use_the_external_store(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "Target"
            repository.mkdir()
            store = root / "external-store"
            profile = approved_profile(repository, store)
            with mock.patch.dict(os.environ, {"UQA_PROFILES_DIR": str(store)}):
                self.assertEqual([profile], qa_agent.available_profiles())
                self.assertEqual(profile, qa_agent.load_profile(str(repository))[0])

    def test_review_draft_is_not_loaded_as_accepted_knowledge(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "PendingReview"
            repository.mkdir()
            profile = qa_agent.profile_path(repository, root / "profiles")
            profile.mkdir(parents=True)
            (profile / "profile.yaml").write_text("draft", encoding="utf-8")

            with self.assertRaises(FileNotFoundError):
                qa_agent.load_profile(str(repository), root / "profiles")


class ProfileCommandTests(unittest.TestCase):
    def test_profile_path_uses_cli_store_without_creating_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            repository = root / "Target"
            repository.mkdir()
            store = root / "saved knowledge"
            output = io.StringIO()
            argv = ["qa-agent", "--profiles-dir", str(store), "profile-path", "--repo", str(repository)]
            with mock.patch("sys.argv", argv), mock.patch.dict(os.environ, {"UQA_PROFILES_DIR": str(root / "other")}), contextlib.redirect_stdout(output):
                self.assertEqual(0, qa_agent.main())
            self.assertEqual(str(qa_agent.profile_path(repository, store)), output.getvalue().strip())
            self.assertFalse(store.exists())

    def test_profile_path_rejects_missing_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            argv = ["qa-agent", "--profiles-dir", str(root / "store"), "profile-path", "--repo", str(root / "missing")]
            with mock.patch("sys.argv", argv), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(2, qa_agent.main())


class SkillInstallerTests(unittest.TestCase):
    def test_installs_links_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for skill in agent_installer.SKILLS:
                source = root / "skills" / skill
                source.mkdir(parents=True)
                (source / "SKILL.md").write_text(skill, encoding="utf-8")
            skills_root = root / "user" / ".agents" / "skills"

            links = agent_installer.install_skill_root(root, skills_root)
            agent_installer.install_skill_root(root, skills_root)

            self.assertEqual(2, len(links))
            for source, destination in links:
                self.assertEqual(source.resolve(), destination.resolve())

    def test_refuses_to_replace_unrelated_skill_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for skill in agent_installer.SKILLS:
                source = root / "skills" / skill
                source.mkdir(parents=True)
                (source / "SKILL.md").write_text(skill, encoding="utf-8")
            skills_root = root / "user" / ".agents" / "skills"
            skills_root.mkdir(parents=True)
            destination = skills_root / agent_installer.SKILLS[0]
            destination.mkdir()

            with self.assertRaises(FileExistsError):
                agent_installer.install_skill_root(root, skills_root)

    def test_replaces_dangling_legacy_skill_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            skills_root = root / "user" / ".agents" / "skills"
            skills_root.mkdir(parents=True)
            for skill in agent_installer.SKILLS:
                source = root / "skills" / skill
                source.mkdir(parents=True)
                (source / "SKILL.md").write_text(skill, encoding="utf-8")
                legacy_source = root / "agent-adapters" / "codex" / "skills" / skill
                (skills_root / skill).symlink_to(legacy_source, target_is_directory=True)

            links = agent_installer.install_skill_root(root, skills_root)

            for source, destination in links:
                self.assertTrue(destination.is_dir())
                self.assertEqual(source.resolve(), destination.resolve())


class AgentInstallerTests(unittest.TestCase):
    def create_source(self, root):
        for skill in agent_installer.SKILLS:
            source = root / "skills" / skill
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text(skill, encoding="utf-8")

    def test_default_installation_keeps_claude_and_copilot_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.create_source(root)
            home = root / "home"

            links = agent_installer.install_skills(root, home)

            self.assertEqual({"Claude Code", "GitHub Copilot"}, {host for host, _, _ in links})
            self.assertEqual(4, len(links))
            self.assertFalse((home / ".agents").exists())
            for _, source, destination in links:
                self.assertEqual(source.resolve(), destination.resolve())

    def test_agent_selection_installs_only_the_selected_host(self):
        hosts = {
            "codex": ("Codex", Path(".agents/skills")),
            "claude": ("Claude Code", Path(".claude/skills")),
            "copilot": ("GitHub Copilot", Path(".copilot/skills")),
        }
        for agent, (host, directory) in hosts.items():
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                self.create_source(root)
                home = root / "home"

                links = agent_installer.install_skills(root, home, agent=agent)

                self.assertEqual({host}, {name for name, _, _ in links})
                self.assertEqual(2, len(links))
                for _, source, destination in links:
                    self.assertEqual(home / directory / source.name, destination)
                    self.assertEqual(source.resolve(), destination.resolve())
                for other, (_, other_directory) in hosts.items():
                    if other != agent:
                        self.assertFalse((home / other_directory).exists())

    def test_default_install_preflights_all_hosts_before_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.create_source(root)
            home = root / "home"
            occupied = home / ".copilot/skills" / agent_installer.SKILLS[0]
            occupied.mkdir(parents=True)

            with self.assertRaises(FileExistsError):
                agent_installer.install_skills(root, home)

            self.assertFalse((home / ".claude").exists())
            self.assertTrue(occupied.is_dir())

    def test_cli_routes_agent_selection(self):
        with mock.patch.object(agent_installer, "install_skills", return_value=[]) as install, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, agent_installer.main(["--agent", "copilot"]))
        self.assertEqual("copilot", install.call_args.kwargs["agent"])

    def test_codex_cli_selects_codex(self):
        with mock.patch.object(agent_installer, "install_skills", return_value=[]) as install, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, agent_installer.main(["--agent", "codex"]))
        self.assertEqual("codex", install.call_args.kwargs["agent"])


class PluginPackageTests(unittest.TestCase):
    def create_source(self, root):
        files = (
            "plugin.json",
            "skills/qa-onboard-repo/SKILL.md",
            "skills/jira-test-generator/SKILL.md",
            "schemas/repository-profile.schema.json",
            "schemas/automation-plan.schema.json",
            "schemas/requirement-analysis.schema.json",
            "schemas/test-case.schema.json",
            "scripts/qa_agent.py",
            "requirements-core.txt",
            "repo-profiles/template/profile.yaml",
            "repo-profiles/template/conventions.md",
            "repo-profiles/template/patterns.md",
        )
        for filename in files:
            path = root / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(filename, encoding="utf-8")
        return files

    def test_manifest_and_workflows_are_packaged_together(self):
        root = SCRIPT.parents[1]
        manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual("universal-qa-agent", manifest["name"])
        self.assertEqual("https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", manifest["$schema"])
        for skill in agent_installer.SKILLS:
            self.assertTrue((root / "skills" / skill / "SKILL.md").is_file())
        self.assertTrue((root / "schemas" / "repository-profile.schema.json").is_file())

    def test_distribution_includes_resources_and_excludes_private_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / "source"
            files = self.create_source(source)
            excluded = (
                "repo-profiles/PrivateProject/secret-draft.md",
                "scripts/install_agent_skills.py",
                "skills/qa-onboard-repo/__pycache__/helper.pyc",
                "skills/jira-test-generator/helper.pyc",
                "README.md",
            )
            for filename in excluded:
                path = source / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("must not ship", encoding="utf-8")

            destination = packager.package_plugin(source, root / "dist")

            self.assertEqual(root / "dist" / "universal-qa-agent", destination)
            for filename in files:
                self.assertEqual(filename, (destination / filename).read_text(encoding="utf-8"))
            for filename in excluded:
                self.assertFalse((destination / filename).exists())

    def test_distribution_refuses_to_replace_existing_destination(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / "source"
            self.create_source(source)
            destination = root / "dist" / "universal-qa-agent"
            destination.mkdir(parents=True)
            sentinel = destination / "keep.txt"
            sentinel.write_text("existing", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                packager.package_plugin(source, root / "dist")

            self.assertEqual("existing", sentinel.read_text(encoding="utf-8"))

    def test_distribution_checks_required_sources_before_copying(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / "source"
            self.create_source(source)
            (source / "scripts" / "qa_agent.py").unlink()

            with self.assertRaises(FileNotFoundError):
                packager.package_plugin(source, root / "dist")

            self.assertFalse((root / "dist" / "universal-qa-agent").exists())


if __name__ == "__main__":
    unittest.main()
