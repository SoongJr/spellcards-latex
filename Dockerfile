# This dockerfile is used for VS Code dev-containers and GitHub Codespaces. May not work properly for building the PDF directly.
FROM miktex/miktex:essential AS devcontainer

# Install packages with apt, then clean up temporary apt files
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y \
    git locales pandoc \
    latexmk libyaml-tiny-perl libfile-homedir-perl; \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set locale to US English
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Finish configuration of miktex
RUN miktexsetup --verbose --shared=yes finish # must be done before changing the config
RUN initexmf --admin --set-config-value [MPM]AutoAdmin=t
RUN initexmf --admin --set-config-value [MPM]AutoInstall=t

# # Switch to non-priviliged user, this also tells the Codespace to run as this user
# USER miktex
# deliberately staying root as Docker Desktop also runs as root on Windows.
# We might want the opposite on Linux though... TBD

FROM devcontainer AS latexmk

# Update LaTeX packages to latest version
RUN miktex --admin packages update-package-database && miktex --admin packages update

# Generate the PDF when the docker container runs
# (user is expected to mount their workspace to /miktex/work as intended by base image miktex/miktex)
ENTRYPOINT ["latexmk", "-pdf", "-pv-", "-interaction=nonstopmode", "-halt-on-error", "-shell-escape", "src/spellcards.tex"]

# Recommended command for building and running this image:
# docker build --target latexmk --tag spellcards:latest .
# Windows: stay as root (additional slashes in front of paths are for use on Windows with gitBash as parameter get handed over to docker.exe)
#   docker run --name spellcards-build --rm --volume "/$(pwd)://miktex/work" spellcards:latest
# Linux: run as (anonymous) user with same ID as the one on host
#   docker run --name spellcards-build --rm --user "$(id -u):$(id -g)" --volume "$(pwd):/miktex/work" spellcards:latest
