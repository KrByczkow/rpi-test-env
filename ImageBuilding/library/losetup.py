#!/usr/bin/python

import os.path

from ansible.module_utils.basic import *


def get_partitions(block_device):
    partitions = []

    time.sleep(1)
    subprocess.run(['udevadm', 'settle', block_device])

    for entry in os.listdir('/dev'):
        if entry == block_device:
            continue

        if entry.startswith(block_device + 'p'):
            partitions.append('/dev/%s' % entry)

    partitions.sort()

    return partitions


class Losetup(object):
    def __init__(self, module):
        self.module = module
        self.image = module.params['image']
        self.action = module.params['action']
        self.losetup_cmd = module.get_bin_path('losetup', True)

    def _image_mount_path(self):
        rc, out, err = self.module.run_command('%s -J' % self.losetup_cmd)
        if rc != 0:
            return None, None

        json_data = json.loads(out)
        for device in json_data['loopdevices']:
            if device['back-file'] is None:
                return None, None

            if os.path.abspath(self.image) == os.path.abspath(device["back-file"]):
                return device['name'], device['back-file']

        return None, None

    def create_device(self):
        (rc, out, err) = self.module.run_command('%s -f -P --show %s' % (self.losetup_cmd, self.image))
        if rc != 0:
            return None, False, rc, out + err

        return out.strip(), True, 0, None

    def detach_device(self, nm):
        (rc, out, err) = self.module.run_command('%s -d %s' % (self.losetup_cmd, nm))
        if rc != 0:
            return None, False, rc, out + err

        return None, True, 0, None

    def device_block(self):
        d1, d2 = self._image_mount_path()
        if d2 is not None:
            if self.action == 'detach':
                return self.detach_device(d1)

            return d1, False, 0, None

        if self.action == 'attach':
            return self.create_device()
        elif self.action == 'detach':
            return None, False, 1, "Image not mounted"

        raise RuntimeError("Unknown action \"" + self.action + "\"")


def main():
    mod_args = dict(
        image=dict(type='str', required=True),
        action=dict(type='str', required=False, default='attach')
    )

    module = AnsibleModule(argument_spec=mod_args, supports_check_mode=True)

    # Check if image is already mounted
    # If it's not mounted, mount the image
    # Return its device (i.e. /dev/loop4) by running `losetup --show -f -P disk.img`

    result = dict(
        changed=False,
        device='',  # '/dev/loop1'
        partitions=[],  # [ '/dev/loop1p1', '/dev/loop1p2', ... ]
    )

    lo_mod = Losetup(module)
    dev, changed, rc, err = lo_mod.device_block()
    if rc != 0:
        module.fail_json(msg='Failed to create device, exit code %d, err = %s' % (rc, err))

    partitions = []

    if lo_mod.action == 'attach':
        partitions = get_partitions(os.path.basename(dev))

    result['device'] = dev
    result['partitions'] = partitions
    result['changed'] = changed

    module.exit_json(**result)


if __name__ == '__main__':
    main()

# import epdb; epdb.serve()
