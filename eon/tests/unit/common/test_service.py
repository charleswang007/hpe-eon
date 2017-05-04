#
# (c) Copyright 2015-2017 Hewlett Packard Enterprise Development Company LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#.

import mock
import os
import fixtures
from oslo_config import cfg

from eon.tests.unit.base_test import TestCase
from eon.common import service

CONF = cfg.CONF


class TestWSGIService(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.policy_dir = self.useFixture(fixtures.TempDir())
        self.policy_file_name = os.path.join(self.policy_dir.path,
                                             'policy.json')
        with open(self.policy_file_name, 'w') as fp:
            fp.write("""{"a": "b"}""")
        CONF.set_override('policy_file', self.policy_file_name)

    @mock.patch.object(service.app, 'VersionSelectorApplication')
    def test_reset_pool_size_to_default(self, mock_app):
        test_service = service.WSGIService("test_service")
        test_service.start()

        # Stopping the service, which in turn sets pool size to 0
        test_service.stop()
        self.assertEqual(0, test_service.server._pool.size)

        # Resetting pool size to default
        test_service.reset()
        test_service.start()
        self.assertTrue(test_service.server._pool.size > 0)
        self.assertTrue(mock_app.called)

    @mock.patch.object(service.wsgi, 'Server')
    def test_workers_set_correct_setting(self, wsgi_server):
        self.config(api_workers=8, group='api')
        self.config(auditing=False)
        test_service = service.WSGIService("eon-api")
        self.assertEqual(8, test_service.workers)
