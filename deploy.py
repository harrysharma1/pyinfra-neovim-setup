from pyinfra.context import host
from pyinfra.facts.files import Directory
from pyinfra.facts.server import Home
from pyinfra.operations import apt, files, server

NEOVIM_VERSION = "v0.12.4"
NEOVIM_URL = f"https://github.com/neovim/neovim/releases/download/{NEOVIM_VERSION}/nvim-linux-x86_64.tar.gz"
NEOVIM_SHA256SUM = "012bf3fcac5ade43914df3f174668bf64d05e049a4f032a388c027b1ebd78628"


apt.packages(
        packages = ["vim", "curl", "ripgrep", "unzip"],
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


shell_home = host.get_fact(Home, _sudo = False)

files.line(
    name = "Writing the nvim binary to path",
    path = f"{shell_home}/.bashrc",
    line = 'export PATH="$PATH:/opt/nvim-linux-x86_64/bin"',
    present = True
)


