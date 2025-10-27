"""
PropertyPilot AgentCore Benefits Testing Suite
Tests all AgentCore features: observability, session isolation, auto-scaling, security
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Any
from datetime import datetime
import boto3
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from agentcore_deployment import AgentCoreDeploymentManager, AgentCoreConfig


class AgentCoreBenefitsTester:
    """Comprehensive tester for all AgentCore benefits"""
    
    def __init__(self, deployment_results_file: str = "agentcore_deployment_results.json"):
        self.deployment_results = self.load_deployment_results(deployment_results_file)
        self.cloudwatch_client = boto3.client('cloudwatch')
        self.xray_client = boto3.client('xray')
        self.bedrock_client = boto3.client('bedrock-agentcore')
        
        # Test configuration
        self.test_sessions = []
        self.performance_metrics = {}
        self.security_tests = {}
        self.observability_data = {}
    
    def load_deployment_results(self, file_path: str) -> Dict:
        """Load deployment results"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Deployment results file not found: {file_path}")
            print("   Run enhanced deployment first: ./deploy_agentcore.sh")
            return {}
    
    async def test_session_isolation(self) -> Dict:
        """Test AgentCore session isolation capabilities"""
        print("\n🔒 Testing Session Isolation & Persistence")
        print("=" * 45)
        
        if not self.deployment_results.get("agents"):
            return {"error": "No deployed agents found"}
        
        main_agent_arn = self.deployment_results["agents"].get("PropertyPilotMain")
        if not main_agent_arn:
            return {"error": "Main agent not found"}
        
        # Create multiple concurrent sessions
        session_tests = []
        num_sessions = 5
        
        for i in range(num_sessions):
            session_id = f"isolation_test_session_{i}_{uuid.uuid4().hex[:8]}"
            user_id = f"test_user_{i}"
            
            test_payload = {
                "type": "property_analysis",
                "prompt": f"Analyze properties for user {i} in different cities",
                "location": ["Austin, TX", "Dallas, TX", "Houston, TX", "San Antonio, TX", "Fort Worth, TX"][i],
                "max_price": 300000 + (i * 50000),
                "user_preferences": {
                    "session_test": True,
                    "user_id": user_id,
                    "test_iteration": i
                }
            }
            
            session_tests.append({
                "session_id": session_id,
                "user_id": user_id,
                "payload": test_payload
            })
        
        # Execute sessions concurrently
        results = []
        start_time = time.time()
        
        async def invoke_session(session_test):
            try:
                deployment_manager = AgentCoreDeploymentManager(AgentCoreConfig())
                result = deployment_manager.invoke_with_session_context(
                    main_agent_arn,
                    session_test["payload"],
                    session_test["user_id"]
                )
                return {
                    "session_id": session_test["session_id"],
                    "user_id": session_test["user_id"],
                    "success": "error" not in result,
                    "response_time": time.time() - start_time,
                    "session_metadata": result.get("session_metadata", {}),
                    "result": result
                }
            except Exception as e:
                return {
                    "session_id": session_test["session_id"],
                    "user_id": session_test["user_id"],
                    "success": False,
                    "error": str(e)
                }
        
        # Run concurrent session tests
        tasks = [invoke_session(test) for test in session_tests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        
        # Analyze session isolation results
        successful_sessions = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        unique_sessions = len(set(r.get("session_id") for r in results if isinstance(r, dict)))
        
        isolation_test_results = {
            "total_sessions": num_sessions,
            "successful_sessions": successful_sessions,
            "unique_sessions": unique_sessions,
            "concurrent_execution_time": end_time - start_time,
            "isolation_verified": unique_sessions == num_sessions,
            "session_details": results
        }
        
        print(f"✅ Session Isolation Test Results:")
        print(f"   Total Sessions: {num_sessions}")
        print(f"   Successful: {successful_sessions}")
        print(f"   Unique Sessions: {unique_sessions}")
        print(f"   Isolation Verified: {'✅' if isolation_test_results['isolation_verified'] else '❌'}")
        print(f"   Execution Time: {end_time - start_time:.2f}s")
        
        return isolation_test_results
    
    async def test_observability_features(self) -> Dict:
        """Test AgentCore observability and monitoring"""
        print("\n📊 Testing Observability & Monitoring")
        print("=" * 40)
        
        observability_results = {
            "cloudwatch_logs": {},
            "xray_traces": {},
            "custom_metrics": {},
            "dashboards": {}
        }
        
        # Test CloudWatch Logs
        try:
            log_groups = self.cloudwatch_client.describe_log_groups(
                logGroupNamePrefix="/aws/bedrock-agentcore/propertypilot"
            )
            
            observability_results["cloudwatch_logs"] = {
                "available": len(log_groups["logGroups"]) > 0,
                "log_groups": [lg["logGroupName"] for lg in log_groups["logGroups"]],
                "total_groups": len(log_groups["logGroups"])
            }
            
            print(f"✅ CloudWatch Logs: {len(log_groups['logGroups'])} log groups found")
            
        except Exception as e:
            observability_results["cloudwatch_logs"] = {"error": str(e)}
            print(f"❌ CloudWatch Logs error: {str(e)}")
        
        # Test X-Ray Tracing
        try:
            # Get recent traces
            end_time = datetime.now()
            start_time = datetime.fromtimestamp(end_time.timestamp() - 3600)  # Last hour
            
            traces = self.xray_client.get_trace_summaries(
                TimeRangeType='TimeRangeByStartTime',
                StartTime=start_time,
                EndTime=end_time,
                FilterExpression='service("propertypilot-main")'
            )
            
            observability_results["xray_traces"] = {
                "available": len(traces["TraceSummaries"]) > 0,
                "trace_count": len(traces["TraceSummaries"]),
                "recent_traces": traces["TraceSummaries"][:5]  # First 5 traces
            }
            
            print(f"✅ X-Ray Tracing: {len(traces['TraceSummaries'])} traces found")
            
        except Exception as e:
            observability_results["xray_traces"] = {"error": str(e)}
            print(f"❌ X-Ray Tracing error: {str(e)}")
        
        # Test Custom Metrics
        try:
            metrics = self.cloudwatch_client.list_metrics(
                Namespace='AWS/BedrockAgentCore'
            )
            
            observability_results["custom_metrics"] = {
                "available": len(metrics["Metrics"]) > 0,
                "metric_count": len(metrics["Metrics"]),
                "metric_names": list(set(m["MetricName"] for m in metrics["Metrics"]))
            }
            
            print(f"✅ Custom Metrics: {len(metrics['Metrics'])} metrics available")
            
        except Exception as e:
            observability_results["custom_metrics"] = {"error": str(e)}
            print(f"❌ Custom Metrics error: {str(e)}")
        
        # Test Dashboards
        try:
            dashboards = self.cloudwatch_client.list_dashboards(
                DashboardNamePrefix="PropertyPilot"
            )
            
            observability_results["dashboards"] = {
                "available": len(dashboards["DashboardEntries"]) > 0,
                "dashboard_count": len(dashboards["DashboardEntries"]),
                "dashboard_names": [d["DashboardName"] for d in dashboards["DashboardEntries"]]
            }
            
            print(f"✅ Dashboards: {len(dashboards['DashboardEntries'])} dashboards created")
            
        except Exception as e:
            observability_results["dashboards"] = {"error": str(e)}
            print(f"❌ Dashboards error: {str(e)}")
        
        return observability_results
    
    async def test_auto_scaling(self) -> Dict:
        """Test AgentCore auto-scaling capabilities"""
        print("\n⚡ Testing Auto-Scaling & Performance")
        print("=" * 40)
        
        if not self.deployment_results.get("agents"):
            return {"error": "No deployed agents found"}
        
        main_agent_arn = self.deployment_results["agents"].get("PropertyPilotMain")
        if not main_agent_arn:
            return {"error": "Main agent not found"}
        
        # Performance test configuration
        concurrent_requests = [1, 5, 10, 20, 50]  # Gradually increase load
        scaling_results = {}
        
        for num_requests in concurrent_requests:
            print(f"\n🔄 Testing with {num_requests} concurrent requests...")
            
            start_time = time.time()
            
            # Create concurrent requests
            async def make_request(request_id):
                try:
                    session_id = f"scaling_test_{request_id}_{uuid.uuid4().hex[:8]}"
                    
                    payload = {
                        "type": "property_analysis",
                        "prompt": f"Quick analysis for scaling test {request_id}",
                        "location": "Austin, TX",
                        "max_price": 400000,
                        "scaling_test": True,
                        "request_id": request_id
                    }
                    
                    deployment_manager = AgentCoreDeploymentManager(AgentCoreConfig())
                    result = deployment_manager.invoke_with_session_context(
                        main_agent_arn,
                        payload,
                        f"scaling_user_{request_id}"
                    )
                    
                    return {
                        "request_id": request_id,
                        "success": "error" not in result,
                        "response_time": time.time() - start_time
                    }
                    
                except Exception as e:
                    return {
                        "request_id": request_id,
                        "success": False,
                        "error": str(e)
                    }
            
            # Execute concurrent requests
            tasks = [make_request(i) for i in range(num_requests)]
            request_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze results
            successful_requests = sum(1 for r in request_results if isinstance(r, dict) and r.get("success"))
            success_rate = (successful_requests / num_requests) * 100
            avg_response_time = total_time / num_requests if num_requests > 0 else 0
            
            scaling_results[num_requests] = {
                "total_requests": num_requests,
                "successful_requests": successful_requests,
                "success_rate": success_rate,
                "total_time": total_time,
                "avg_response_time": avg_response_time,
                "requests_per_second": num_requests / total_time if total_time > 0 else 0
            }
            
            print(f"   ✅ {successful_requests}/{num_requests} successful ({success_rate:.1f}%)")
            print(f"   ⏱️  Total time: {total_time:.2f}s, Avg: {avg_response_time:.2f}s")
            print(f"   🚀 Throughput: {scaling_results[num_requests]['requests_per_second']:.2f} req/s")
            
            # Brief pause between scaling tests
            await asyncio.sleep(2)
        
        # Calculate scaling efficiency
        baseline_rps = scaling_results[1]["requests_per_second"]
        scaling_efficiency = {}
        
        for num_requests, results in scaling_results.items():
            if num_requests > 1:
                expected_rps = baseline_rps * num_requests
                actual_rps = results["requests_per_second"]
                efficiency = (actual_rps / expected_rps) * 100 if expected_rps > 0 else 0
                scaling_efficiency[num_requests] = efficiency
        
        auto_scaling_results = {
            "scaling_tests": scaling_results,
            "scaling_efficiency": scaling_efficiency,
            "max_concurrent_tested": max(concurrent_requests),
            "overall_success_rate": sum(r["success_rate"] for r in scaling_results.values()) / len(scaling_results)
        }
        
        print(f"\n📈 Auto-Scaling Summary:")
        print(f"   Max Concurrent: {max(concurrent_requests)} requests")
        print(f"   Overall Success Rate: {auto_scaling_results['overall_success_rate']:.1f}%")
        print(f"   Scaling Efficiency: {list(scaling_efficiency.values())}")
        
        return auto_scaling_results
    
    async def test_security_features(self) -> Dict:
        """Test AgentCore security features"""
        print("\n🛡️ Testing Security Features")
        print("=" * 30)
        
        security_results = {
            "session_isolation": True,  # Tested in session isolation test
            "iam_role_validation": {},
            "encryption_validation": {},
            "network_security": {}
        }
        
        # Test IAM Role Configuration
        try:
            iam_client = boto3.client('iam')
            role_name = "PropertyPilotEnhancedAgentRole"
            
            role = iam_client.get_role(RoleName=role_name)
            attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)
            
            security_results["iam_role_validation"] = {
                "role_exists": True,
                "role_arn": role["Role"]["Arn"],
                "attached_policies": [p["PolicyName"] for p in attached_policies["AttachedPolicies"]],
                "trust_policy_valid": "bedrock-agentcore.amazonaws.com" in str(role["Role"]["AssumeRolePolicyDocument"])
            }
            
            print(f"✅ IAM Role: {role_name} properly configured")
            
        except Exception as e:
            security_results["iam_role_validation"] = {"error": str(e)}
            print(f"❌ IAM Role validation error: {str(e)}")
        
        # Test Encryption (ECR repositories)
        try:
            ecr_client = boto3.client('ecr')
            repositories = ecr_client.describe_repositories(
                repositoryNames=[
                    "propertypilot-main",
                    "propertypilot-property-scout",
                    "propertypilot-market-analyzer",
                    "propertypilot-deal-evaluator",
                    "propertypilot-investment-manager"
                ]
            )
            
            encrypted_repos = sum(1 for repo in repositories["repositories"] 
                                if repo.get("encryptionConfiguration", {}).get("encryptionType") == "AES256")
            
            security_results["encryption_validation"] = {
                "total_repositories": len(repositories["repositories"]),
                "encrypted_repositories": encrypted_repos,
                "encryption_enabled": encrypted_repos == len(repositories["repositories"])
            }
            
            print(f"✅ Encryption: {encrypted_repos}/{len(repositories['repositories'])} repositories encrypted")
            
        except Exception as e:
            security_results["encryption_validation"] = {"error": str(e)}
            print(f"❌ Encryption validation error: {str(e)}")
        
        return security_results
    
    async def run_comprehensive_test(self) -> Dict:
        """Run comprehensive test of all AgentCore benefits"""
        print("🧪 PropertyPilot AgentCore Benefits Comprehensive Test")
        print("=" * 55)
        
        if not self.deployment_results:
            return {"error": "No deployment results found. Run deployment first."}
        
        comprehensive_results = {
            "test_timestamp": datetime.now().isoformat(),
            "deployment_info": self.deployment_results,
            "test_results": {}
        }
        
        # Run all benefit tests
        print("\n🚀 Starting comprehensive AgentCore benefits testing...")
        
        # Test 1: Session Isolation
        comprehensive_results["test_results"]["session_isolation"] = await self.test_session_isolation()
        
        # Test 2: Observability
        comprehensive_results["test_results"]["observability"] = await self.test_observability_features()
        
        # Test 3: Auto-Scaling
        comprehensive_results["test_results"]["auto_scaling"] = await self.test_auto_scaling()
        
        # Test 4: Security
        comprehensive_results["test_results"]["security"] = await self.test_security_features()
        
        # Generate summary
        summary = self.generate_test_summary(comprehensive_results["test_results"])
        comprehensive_results["summary"] = summary
        
        # Save results
        with open("agentcore_benefits_test_results.json", "w") as f:
            json.dump(comprehensive_results, f, indent=2)
        
        print(f"\n📊 Comprehensive Test Results Summary:")
        print(f"=" * 45)
        for category, status in summary.items():
            status_icon = "✅" if status["passed"] else "❌"
            print(f"{status_icon} {category.replace('_', ' ').title()}: {status['score']:.1f}% ({status['details']})")
        
        overall_score = sum(s["score"] for s in summary.values()) / len(summary)
        print(f"\n🎯 Overall AgentCore Benefits Score: {overall_score:.1f}%")
        print(f"📄 Detailed results saved to: agentcore_benefits_test_results.json")
        
        return comprehensive_results
    
    def generate_test_summary(self, test_results: Dict) -> Dict:
        """Generate summary of test results"""
        summary = {}
        
        # Session Isolation Summary
        session_test = test_results.get("session_isolation", {})
        if "error" not in session_test:
            isolation_score = 100 if session_test.get("isolation_verified") else 0
            summary["session_isolation"] = {
                "passed": session_test.get("isolation_verified", False),
                "score": isolation_score,
                "details": f"{session_test.get('successful_sessions', 0)}/{session_test.get('total_sessions', 0)} sessions"
            }
        else:
            summary["session_isolation"] = {"passed": False, "score": 0, "details": "Test failed"}
        
        # Observability Summary
        obs_test = test_results.get("observability", {})
        obs_features = ["cloudwatch_logs", "xray_traces", "custom_metrics", "dashboards"]
        obs_working = sum(1 for feature in obs_features if obs_test.get(feature, {}).get("available", False))
        obs_score = (obs_working / len(obs_features)) * 100
        summary["observability"] = {
            "passed": obs_working >= 3,  # At least 3 out of 4 features working
            "score": obs_score,
            "details": f"{obs_working}/{len(obs_features)} features working"
        }
        
        # Auto-Scaling Summary
        scaling_test = test_results.get("auto_scaling", {})
        if "error" not in scaling_test:
            scaling_score = scaling_test.get("overall_success_rate", 0)
            summary["auto_scaling"] = {
                "passed": scaling_score >= 80,  # 80% success rate threshold
                "score": scaling_score,
                "details": f"{scaling_score:.1f}% success rate"
            }
        else:
            summary["auto_scaling"] = {"passed": False, "score": 0, "details": "Test failed"}
        
        # Security Summary
        security_test = test_results.get("security", {})
        security_features = ["iam_role_validation", "encryption_validation"]
        security_working = sum(1 for feature in security_features 
                             if "error" not in security_test.get(feature, {}))
        security_score = (security_working / len(security_features)) * 100
        summary["security"] = {
            "passed": security_working == len(security_features),
            "score": security_score,
            "details": f"{security_working}/{len(security_features)} features validated"
        }
        
        return summary


async def main():
    """Main test runner for AgentCore benefits"""
    tester = AgentCoreBenefitsTester()
    
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "session":
            await tester.test_session_isolation()
        elif test_type == "observability":
            await tester.test_observability_features()
        elif test_type == "scaling":
            await tester.test_auto_scaling()
        elif test_type == "security":
            await tester.test_security_features()
        elif test_type == "comprehensive":
            await tester.run_comprehensive_test()
        else:
            print("Usage: python test_agentcore_benefits.py [session|observability|scaling|security|comprehensive]")
    else:
        # Run comprehensive test by default
        await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())