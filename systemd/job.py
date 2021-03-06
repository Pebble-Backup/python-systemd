#
# Copyright (c) 2010 Mandriva
#
# This file is part of python-systemd.
#
# python-systemd is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# python-systemd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import dbus
import dbus.mainloop.glib

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

from systemd.property import Property
from systemd.exceptions import SystemdError

class Job(object):
    """Abstraction class to org.freedesktop.systemd1.Job interface"""

    def __init__(self, job_path):
        self.__bus = dbus.SystemBus()
        self.__proxy = self.__bus.get_object(
            'org.freedesktop.systemd1',
            job_path,
        )
        self.__interface = dbus.Interface(
            self.__proxy,
            'org.freedesktop.systemd1.Job',
        )

        self.__properties_interface = dbus.Interface(
            self.__proxy,
            'org.freedesktop.DBus.Properties')

        self.__properties()

    def __properties(self):
        properties = self.__properties_interface.GetAll(
            self.__interface.dbus_interface)
        attr_property = Property()
        for key, value in properties.items():
            setattr(attr_property, key, value)
        setattr(self, 'properties', attr_property)

    def cancel(self):
        try:
            self.__interface.Cancel()
        except dbus.exceptions.DBusException, error:
            raise SystemdError(error)

    @staticmethod
    def if_exists(job_path):
        try:
            return Job(job_path)
        except dbus.exceptions.DBusException as error:
            error_str = str(error)
            if "Unknown interface 'org.freedesktop.systemd1.Job'." in error_str:
                return None
            if "org.freedesktop.DBus.Error.UnknownObject" in error_str:
                return None
            raise