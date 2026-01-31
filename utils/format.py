import subprocess
import sys
from pathlib import Path

# 查找指定扩展名的文件
def files(dir, exts):
    files = []
    for ext in exts:
        files.extend(Path(dir).rglob(f"*{ext}"))
    return files

# 检查 clang-format 是否可用
def check_clangformat():
    try:
        subprocess.run(["clang-format", "--version"], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("It seems that clang-format is not installed.")
        if sys.platform == "win32":
            print("You are on Windows so you can add it through WinGet:")
            print("    winget LLVM.ClangFormat")
        sys.exit(1)

def main():
    check_clangformat()
    for path in files(dir = "../Chess98", exts=[".hpp", ".cpp"]):
        subprocess.run(["clang-format", "-i", str(path)], check=True)
    print("Done")

if __name__ == "__main__":
    main()
