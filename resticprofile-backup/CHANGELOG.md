## 1.3.1

- Fix mounting by UUID and label

## 1.3.0

- Properly unmount network shares on container shutdown
- Update restic to 0.18.1
- Add new option `localdisks` which enables mounting local disks for backups (USB drives, secondary drives,...)
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
