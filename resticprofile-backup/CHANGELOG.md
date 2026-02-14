# Unreleased

- update dependency libwbclient to v4.22.6-r0 (#59)

- update dependency readline to v8.3.1-r0 (#60)

- update dependency yq-go to v4.49.2-r3 (#61)

- update dependency libpq to v18 (#62)

- update dependency libncursesw to v6.5_p20251123-r0 (#53)

- update dependency lsblk to v2.41.2-r0 (#54)

- update dependency rclone to v1.73.0 (#49)

- update dependency yq-go to v4.47.2-r3 (#47)

# 1.3.11

- update dependency rclone to v1.72.1 (#45)

# 1.3.10

- update dependency yq-go to v4.47.2-r2 (#43)
- update dependency rclone to v1.72.0 (#41)

## 1.3.9

- update postgresql to v17.7-r0

## 1.3.8

- remove builds for armv7, armhf and i386 as unsupported by Home Assistant
  2025.11
- remove codenotary as unsupported by Home Assistant
- update dependency libwbclient to v4.21.9-r1

## 1.3.7

- update dependency rclone to v1.71.2
- update ghcr.io/hassio-addons/base docker tag to v18.2.1

## 1.3.6

- update yq-go dependency to 4.47.2-r1
- update ghcr.io/hassio-addons/base docker tag to v18.2.0

## 1.3.5

- show UUID for available disks too
- update ghcr.io/hassio-addons/base docker tag to v18.1.4

## 1.3.4

- update ghcr.io/hassio-addons/base docker tag to v18.1.3

## 1.3.3

- Update resticprofile to 0.32.0
- update ghcr.io/hassio-addons/base docker tag to v18.1.2

## 1.3.2

- Update rclone to 1.17.1

## 1.3.1

- Fix mounting by UUID and label

## 1.3.0

- Properly unmount network shares on container shutdown
- Update restic to 0.18.1
- Add new option `localdisks` which enables mounting local disks for backups
  (USB drives, secondary drives,...)
- Startup now lists available local disks and supported filesystems in logs

## 1.2.2

- Fix bug in Dockerfile
- Update yq to 4.47.2 again

## 1.2.1

- Mount /share with read-write permission

## 1.2.0

- Use hassio base image for better logging
- Directly download yq instead of installing it from alpine
- Update postgreSQL client to version 17.6
- Update rclone to 1.71.0
- Update yq to 4.47.2

## 1.1.0

- Include postgres-client package in the container

## 1.0.1

- Speed up start, by using restic's snapshot command instead of stats

## 1.0.0

- Add code notary support

## 0.1.1

- Fix missing capability in AppArmor

## 0.1.0

- Initial release
