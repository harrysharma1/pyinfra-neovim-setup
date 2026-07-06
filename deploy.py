from pyinfra.context import host
from pyinfra.facts.files import Directory
from pyinfra.facts.server import Home, User
from pyinfra.operations import apt, files, server, git

NEOVIM_VERSION = "v0.12.4"
NEOVIM_URL = f"https://github.com/neovim/neovim/releases/download/{NEOVIM_VERSION}/nvim-linux-x86_64.tar.gz"
NEOVIM_SHA256SUM = "012bf3fcac5ade43914df3f174668bf64d05e049a4f032a388c027b1ebd78628"


apt.packages(
        packages = ["vim", "curl", "ripgrep", "unzip", "git"],
        update = True,
)

files.download(
        name= f"Downloading neovim@{NEOVIM_VERSION}",
        src= NEOVIM_URL,
        dest= "/tmp/nvim-linux-x86_64.tar.gz",
        sha256sum= NEOVIM_SHA256SUM,
)

files.directory(name="Check if /opt exists", path="/opt")

nvim_opt_exists = True if host.get_fact(Directory, path = "/opt/nvim-linux-x86_64") is not None else False

if not nvim_opt_exists:
    server.shell(
            name = "Extracting nvim tarball to /opt directory",
            commands= ["tar -xzf /tmp/nvim-linux-x86_64.tar.gz -C /opt"]
    )


home = host.get_fact(Home, _sudo = False)
user = host.get_fact(User, _sudo = False)

server.shell(
    name = "Fix ownership of any prior broken user configs from root deployments",
    commands = [
        f"chown {user}:{user} {home}/.bashrc 2>/dev/null || true",
        f"chown -R {user}:{user} {home}/.config/nvim 2>/dev/null || true"
    ]
)

files.line(
    name = "Writing the nvim binary to path",
    path = f"{home}/.bashrc",
    line = 'export PATH="$PATH:/opt/nvim-linux-x86_64/bin"',
    present = True,
    _sudo = False
)

files.directory(
    name = "Ensure ~/.config file exists",
    path = f"{home}/.config/nvim",
    _sudo = False
)

git.repo(
    src = "https://github.com/NvChad/starter",
    dest = f"{home}/.config/nvim",
    _sudo = False
)
