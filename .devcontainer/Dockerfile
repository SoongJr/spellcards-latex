# This dockerfile is used for VS Code dev-containers and GitHub Codespaces. May not work properly for building the PDF directly.
FROM miktex/miktex:essential

# Install packages with apt
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y \
    git jq \
    latexmk libyaml-tiny-perl libfile-homedir-perl pandoc

# Clean up temporary apt files
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Finish configuration of miktex
RUN miktexsetup --verbose --shared=yes finish # must be done before changing the config
RUN initexmf --admin --set-config-value [MPM]AutoAdmin=t
RUN initexmf --admin --set-config-value [MPM]AutoInstall=t

# # Switch to non-priviliged user, this also tells the Codespace to run as this user
# USER miktex
# deliberately staying root as Docker Desktop also runs as root on Windows.
# We might want the opposite on Linux though... TBD
