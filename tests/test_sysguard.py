
import unittest

from modules.system import get_system_info
from modules.processes import get_processes, get_top_memory_processes
from modules.services import classify_service_health
from modules.anomaly import detect_anomalies
from modules.diagnosis import diagnose_incidents
from modules.healing import restart_service


class TestSysGuard(unittest.TestCase):

    def test_system_info_has_valid_readings(self):
        info = get_system_info()

        self.assertIn("hostname", info)
        self.assertIn("cpu_usage", info)
        self.assertIn("memory_usage", info)
        self.assertIn("disk_usage", info)
        self.assertGreaterEqual(info["cpu_usage"], 0)
        self.assertLessEqual(info["cpu_usage"], 100)
        self.assertGreaterEqual(info["memory_usage"], 0)
        self.assertLessEqual(info["memory_usage"], 100)
        self.assertGreaterEqual(info["disk_usage"], 0)
        self.assertLessEqual(info["disk_usage"], 100)

    def test_process_monitoring(self):
        processes = get_processes()
        top = get_top_memory_processes(processes, limit=5)

        self.assertIsInstance(processes, list)
        self.assertLessEqual(len(top), 5)

        if len(top) > 1:
            memory_values = [p["memory"] for p in top]
            self.assertEqual(memory_values, sorted(memory_values, reverse=True))

    def test_service_health_classification(self):
        self.assertEqual(
            classify_service_health({"active_state": "active"}),
            "HEALTHY",
        )
        self.assertEqual(
            classify_service_health({"active_state": "failed"}),
            "FAILED",
        )
        self.assertEqual(
            classify_service_health({"active_state": "inactive"}),
            "INACTIVE",
        )
        self.assertEqual(
            classify_service_health({"status": "not-found"}),
            "UNKNOWN",
        )

    def test_normal_readings_have_no_anomalies(self):
        anomalies = detect_anomalies({
            "cpu_usage": 20,
            "memory_usage": 30,
            "disk_usage": 40,
        })

        self.assertEqual(anomalies, [])

    def test_high_cpu_is_detected(self):
        anomalies = detect_anomalies({
            "cpu_usage": 95,
            "memory_usage": 30,
            "disk_usage": 40,
        })

        self.assertTrue(
            any(item["metric"] == "cpu_usage" for item in anomalies)
        )

    def test_incident_diagnosis(self):
        incidents = diagnose_incidents(
            system_info={
                "cpu_usage": 95,
                "memory_usage": 30,
                "disk_usage": 40,
            },
            processes=[
                {"name": "test-worker", "cpu": 90, "memory": 5}
            ],
            services=[],
            network_results=[],
            anomalies=[
                {
                    "metric": "cpu_usage",
                    "value": 95,
                    "threshold": 80,
                    "severity": "WARNING",
                    "message": "High CPU usage",
                }
            ],
        )

        self.assertTrue(incidents)
        self.assertTrue(
            any(incident["title"] == "High CPU usage"
                for incident in incidents)
        )

    def test_healing_defaults_to_dry_run(self):
        result = restart_service("cron.service")

        self.assertEqual(result["status"], "DRY_RUN")
        self.assertTrue(result["success"])

    def test_healing_requires_approval(self):
        result = restart_service("cron.service", dry_run=False)

        self.assertEqual(result["status"], "APPROVAL_REQUIRED")
        self.assertFalse(result["success"])

    def test_healing_rejects_unapproved_services(self):
        result = restart_service(
            "unapproved.service",
            dry_run=False,
            approved=True,
        )

        self.assertEqual(result["status"], "REJECTED")
        self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
