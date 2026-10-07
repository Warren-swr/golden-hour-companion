"""Check tracked files before publication without opening ignored private inputs."""
import ast
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
PRIVATE_DIRS={'.codex','.claude','.venv','__pycache__','output','work','font_cache'}
MEDIA_SUFFIXES={'.blend','.blend1','.mdd','.mov','.mp4','.zip','.dmg','.otf','.ttf','.woff','.woff2'}
SECRET_PATTERNS=[re.compile(pattern) for pattern in [
    r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{30,}',
    r'sk-[A-Za-z0-9_-]{24,}',r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----']]


def main():
    paths=[Path(name) for name in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0') if name]
    failures=[]
    for relative in paths:
        path=ROOT/relative
        if path.is_symlink() or PRIVATE_DIRS.intersection(relative.parts):failures.append((str(relative),'private path or symlink'))
        if path.suffix.lower() in MEDIA_SUFFIXES or path.name.startswith('.env'):failures.append((str(relative),'excluded asset'))
        if path.stat().st_size>10*1024*1024:failures.append((str(relative),'large Git blob'))
        if path.suffix.lower() in {'.py','.md','.json','.txt','.yml','.yaml'} or path.name in {'.gitignore','.gitattributes'}:
            text=path.read_text()
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):failures.append((str(relative),'credential-like content'))
            if re.search(r'/(?:home|mnt)/'+r'(?:tiger|runs)',text):failures.append((str(relative),'machine-specific path'))
            if re.search(r'(?:bytedance\.com|byted\.org|modelhub\.)',text):failures.append((str(relative),'private infrastructure reference'))
            if path.suffix=='.py':
                try:ast.parse(text,filename=str(relative))
                except SyntaxError:failures.append((str(relative),'Python syntax'))
    if failures:raise SystemExit('\n'.join(f'{name}: {reason}' for name,reason in failures))
    print(f'PUBLIC_TREE_OK: {len(paths)} tracked files; source parses and exclusions pass.')


if __name__=='__main__':main()
