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
INSTALLER_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install_codex_skills.py"
INSTALLER_SPEC = importlib.util.spec_from_file_location("install_codex_skills", INSTALLER_SCRIPT)
installer = importlib.util.module_from_spec(INSTALLER_SPEC)
INSTALLER_SPEC.loader.exec_module(installer)
PACKAGE_SCRIPT = SCRIPT.parent / "package_plugin.py"
PACKAGE_SPEC = importlib.util.spec_from_file_location("package_plugin", PACKAGE_SCRIPT)
packager = importlib.util.module_from_spec(PACKAGE_SPEC)
PACKAGE_SPEC.loader.exec_module(packager)


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
            for name in ("accepted", "draft", "template"):
                profile = root / name
                profile.mkdir(parents=True)
                (profile / "profile.yaml").write_text("profile", encoding="utf-8")
                if name != "draft":
                    (profile / qa_agent.APPROVAL_MARKER).touch()
            self.assertEqual([root / "accepted"], qa_agent.available_profiles(root))

    def test_loads_profile_knowledge_by_repository_folder_name(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "DemoMobileAutomation"
            profile = root / "profiles" / repository.name
            repository.mkdir()
            profile.mkdir(parents=True)
            for name in qa_agent.KNOWLEDGE_FILES:
                (profile / name).write_text(name, encoding="utf-8")
            (profile / qa_agent.APPROVAL_MARKER).touch()

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
            profile = store / repository.name
            profile.mkdir(parents=True)
            (profile / "profile.yaml").write_text("approved", encoding="utf-8")
            (profile / qa_agent.APPROVAL_MARKER).touch()
            with mock.patch.dict(os.environ, {"UQA_PROFILES_DIR": str(store)}):
                self.assertEqual([profile], qa_agent.available_profiles())
                self.assertEqual((profile, [("profile.yaml", "approved")]), qa_agent.load_profile(str(repository)))

    def test_review_draft_is_not_loaded_as_accepted_knowledge(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "PendingReview"
            profile = root / "profiles" / repository.name
            repository.mkdir()
            profile.mkdir(parents=True)
            (profile / "profile.yaml").write_text("draft", encoding="utf-8")

            with self.assertRaises(PermissionError):
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
            self.assertEqual(str(store / "Target"), output.getvalue().strip())
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
            for skill in installer.SKILLS:
                source = root / "skills" / skill
                source.mkdir(parents=True)
                (source / "SKILL.md").write_text(skill, encoding="utf-8")
            skills_root = root / "user" / ".agents" / "skills"

            links = installer.install_skills(root, skills_root)
            installer.install_skills(root, skills_root)

            self.assertEqual(2, len(links))
            for source, destination in links:
                self.assertEqual(source.resolve(), destination.resolve())

    def test_refuses_to_replace_unrelated_skill_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for skill in installer.SKILLS:
                source = root / "skills" / skill
                source.mkdir(parents=True)
                (source / "SKILL.md").write_text(skill, encoding="utf-8")
            skills_root = root / "user" / ".agents" / "skills"
            skills_root.mkdir(parents=True)
            destination = skills_root / installer.SKILLS[0]
            destination.mkdir()

            with self.assertRaises(FileExistsError):
                installer.install_skills(root, skills_root)

    def test_replaces_dangling_legacy_skill_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            skills_root = root / "user" / ".agents" / "skills"
            skills_root.mkdir(parents=True)
            for skill in installer.SKILLS:
                source = root / "skills" / skill
                source.mkdir(parents=True)
                (source / "SKILL.md").write_text(skill, encoding="utf-8")
                legacy_source = root / "agent-adapters" / "codex" / "skills" / skill
                (skills_root / skill).symlink_to(legacy_source, target_is_directory=True)

            links = installer.install_skills(root, skills_root)

            for source, destination in links:
                self.assertTrue(destination.is_dir())
                self.assertEqual(source.resolve(), destination.resolve())


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
        for skill in installer.SKILLS:
            self.assertTrue((root / "skills" / skill / "SKILL.md").is_file())
        self.assertTrue((root / "schemas" / "repository-profile.schema.json").is_file())

    def test_distribution_includes_resources_and_excludes_private_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / "source"
            files = self.create_source(source)
            excluded = (
                "repo-profiles/PrivateProject/secret-draft.md",
                "scripts/install_codex_skills.py",
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
