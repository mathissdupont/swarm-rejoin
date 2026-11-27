# Selected-source note: PX4 Ubuntu and WSL2 setup

- Records: [Ubuntu setup](../../library/px4-ubuntu-setup/README.md), [WSL2 setup](../../library/px4-wsl-setup/README.md); checked 2026-11-27.
- Reading depth: official rendered overview/platform requirements and pinned source Markdown. No installer, build, simulator or graphics/network validation performed.

The official WSL2 guide supports PX4 development through Ubuntu on Windows. The rendered Ubuntu guide lists 24.04/22.04 and Gazebo Harmonic. Its captured source at commit `2fa62338099f18fc3092197e856615eca94d2975` instead lists 22.04/20.04/18.04, including historical simulator references. Do not conflate those versions or present all old commands as current advice. Choose a released PX4 revision and matching Ubuntu/Gazebo/setup instructions when beginning SITL.

The existing multi-vehicle guide separately identifies Linux as the supported environment for Gazebo multi-vehicle simulation. Layer 1 of our proposal is a portable Python model; its portability does not establish that native Windows PX4/Gazebo multi-vehicle operation is supported.

Local `wsl --list --verbose` showed registered Ubuntu and docker-desktop distributions, both stopped, using WSL2. This is a local observation, not source-paper evidence. Ubuntu's actual release and a working SITL toolchain remain unverified. No OS installation, upgrade or simulator launch was performed.

Complete redistributable source Markdown is archived and the unchanged same-commit CC BY license is indexed at its existing location. No official standalone PDFs were located. Existing `px4-multi` files were reused rather than replaced.
