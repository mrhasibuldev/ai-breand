"""
Automated Pipeline Orchestrator

Coordinates autonomous data collection, quality analysis,
and text generation in a seamless pipeline.
"""

import os
import json
import time
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineStage:
    """Represents a stage in the pipeline"""

    def __init__(self, name: str, function, dependencies: List[str] = None):
        """
        Initialize pipeline stage

        Args:
            name: Stage name
            function: Function to execute
            dependencies: List of stage dependencies
        """
        self.name = name
        self.function = function
        self.dependencies = dependencies or []
        self.status = "pending"
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None

    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the stage

        Args:
            context: Pipeline context

        Returns:
            Stage result
        """
        self.status = "running"
        self.start_time = datetime.now()

        try:
            logger.info(f"Executing stage: {self.name}")
            self.result = self.function(context)
            self.status = "completed"
            self.end_time = datetime.now()
            return self.result
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            self.end_time = datetime.now()
            logger.error(f"Stage {self.name} failed: {e}")
            raise

    def get_duration(self) -> float:
        """Get stage duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class AutonomousPipeline:
    """
    Autonomous pipeline that orchestrates data collection,
    quality analysis, and generation without human intervention
    """

    def __init__(self, output_dir: str = "data/pipeline"):
        """
        Initialize autonomous pipeline

        Args:
            output_dir: Output directory for pipeline results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.stages = []
        self.context = {}
        self.pipeline_history = []

        # Initialize components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize pipeline components"""
        from autonomous_collector import AutonomousWebCollector
        from quality_analyzer import DataQualityAnalyzer, AutonomousDecisionMaker
        from self_improving_generator import AutonomousTextGenerator, SelfImprovingSystem

        self.collector = AutonomousWebCollector(str(self.output_dir / "collected"))
        self.analyzer = DataQualityAnalyzer()
        self.decision_maker = AutonomousDecisionMaker(self.analyzer)
        self.generator = AutonomousTextGenerator()
        self.self_improving_system = SelfImprovingSystem()

    def add_stage(self, name: str, function, dependencies: List[str] = None):
        """
        Add a stage to the pipeline

        Args:
            name: Stage name
            function: Stage function
            dependencies: Stage dependencies
        """
        stage = PipelineStage(name, function, dependencies)
        self.stages.append(stage)
        logger.info(f"Added stage: {name}")

    def _collect_data_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage: Collect data"""
        count = context.get("collect_count", 10)
        data_type = context.get("data_type", "qa")

        output_file = self.collector.collect(data_type, count)

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return {
            "data": data,
            "file_path": output_file,
            "count": len(data)
        }

    def _analyze_quality_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage: Analyze data quality"""
        data = context["collect_data"]["data"]

        analysis = self.analyzer.analyze_dataset(data)

        return {
            "analysis": analysis,
            "average_quality": analysis.get("average_quality", 0)
        }

    def _filter_data_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage: Filter data by quality"""
        data = context["collect_data"]["data"]
        avg_quality = context["analyze_quality"]["average_quality"]
        threshold = avg_quality * 0.7

        high_quality, low_quality = self.analyzer.filter_dataset(data, threshold)

        return {
            "high_quality": high_quality,
            "low_quality": low_quality,
            "threshold": threshold,
            "retained_count": len(high_quality),
            "discarded_count": len(low_quality)
        }

    def _learn_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage: Learn from high-quality data"""
        high_quality = context["filter_data"]["high_quality"]

        self.generator.learn(high_quality)

        return {
            "learned_from": len(high_quality),
            "patterns_learned": len(self.generator.pattern_learner.word_patterns)
        }

    def _generate_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage: Generate new data"""
        count = context.get("generate_count", 10)

        generated_data = self.generator.generate_dataset(count)

        # Save generated data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"generated_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(generated_data, f, ensure_ascii=False, indent=2)

        return {
            "generated_data": generated_data,
            "file_path": str(output_file),
            "count": len(generated_data)
        }

    def _validate_generation_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage: Validate generated data quality"""
        generated_data = context["generate"]["generated_data"]

        analysis = self.analyzer.analyze_dataset(generated_data)

        return {
            "analysis": analysis,
            "average_quality": analysis.get("average_quality", 0)
        }

    def _improve_stage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage: Improve system based on feedback"""
        collected_quality = context["analyze_quality"]["average_quality"]
        generated_quality = context["validate_generation"]["average_quality"]

        feedback = {
            "collected_quality": collected_quality,
            "generated_quality": generated_quality,
            "improvement": generated_quality - collected_quality
        }

        self.generator.improve_generation(feedback)

        return {
            "feedback": feedback,
            "improvement": feedback["improvement"]
        }

    def setup_default_pipeline(self):
        """Setup default autonomous pipeline stages"""
        self.add_stage("collect_data", self._collect_data_stage, [])
        self.add_stage("analyze_quality", self._analyze_quality_stage, ["collect_data"])
        self.add_stage("filter_data", self._filter_data_stage, ["analyze_quality"])
        self.add_stage("learn", self._learn_stage, ["filter_data"])
        self.add_stage("generate", self._generate_stage, ["learn"])
        self.add_stage("validate_generation", self._validate_generation_stage, ["generate"])
        self.add_stage("improve", self._improve_stage, ["validate_generation"])

        logger.info("Default pipeline setup completed")

    def execute_pipeline(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the autonomous pipeline

        Args:
            context: Pipeline context

        Returns:
            Pipeline execution results
        """
        if context is None:
            context = {
                "collect_count": 10,
                "generate_count": 10,
                "data_type": "qa"
            }

        self.context = context
        execution_start = datetime.now()

        logger.info("Starting autonomous pipeline execution")

        # Build dependency graph
        stage_order = self._resolve_dependencies()

        # Execute stages in order
        results = {}
        for stage_name in stage_order:
            stage = next(s for s in self.stages if s.name == stage_name)

            # Check if dependencies completed
            for dep in stage.dependencies:
                dep_stage = next(s for s in self.stages if s.name == dep)
                if dep_stage.status != "completed":
                    logger.error(f"Dependency {dep} not completed for stage {stage_name}")
                    raise Exception(f"Dependency {dep} failed")

            # Execute stage
            try:
                result = stage.execute(self.context)
                results[stage_name] = result
                self.context[stage_name] = result
            except Exception as e:
                logger.error(f"Pipeline failed at stage {stage_name}: {e}")
                results["error"] = str(e)
                break

        execution_end = datetime.now()
        duration = (execution_end - execution_start).total_seconds()

        # Build execution summary
        summary = {
            "pipeline_id": f"PIPE_{int(execution_start.timestamp())}",
            "context": context,
            "stage_results": results,
            "stage_durations": {
                stage.name: stage.get_duration() for stage in self.stages
            },
            "total_duration": duration,
            "status": "completed" if "error" not in results else "failed",
            "started_at": execution_start.isoformat(),
            "completed_at": execution_end.isoformat()
        }

        self.pipeline_history.append(summary)

        # Save summary
        self._save_summary(summary)

        logger.info(f"Pipeline execution completed in {duration:.2f}s")
        return summary

    def _resolve_dependencies(self) -> List[str]:
        """
        Resolve stage execution order based on dependencies

        Returns:
            Ordered list of stage names
        """
        # Topological sort
        visited = set()
        order = []

        def visit(stage_name):
            if stage_name in visited:
                return

            stage = next(s for s in self.stages if s.name == stage_name)
            for dep in stage.dependencies:
                visit(dep)

            visited.add(stage_name)
            order.append(stage_name)

        for stage in self.stages:
            visit(stage.name)

        return order

    def _save_summary(self, summary: Dict[str, Any]):
        """Save pipeline execution summary"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.output_dir / f"pipeline_summary_{timestamp}.json"

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(f"Pipeline summary saved to {summary_file}")

    def run_continuous_pipeline(self, cycles: int = 5, interval_seconds: int = 60):
        """
        Run pipeline continuously

        Args:
            cycles: Number of cycles
            interval_seconds: Interval between cycles
        """
        logger.info(f"Starting continuous pipeline ({cycles} cycles, {interval_seconds}s interval)")

        for i in range(cycles):
            logger.info(f"Pipeline cycle {i+1}/{cycles}")

            # Execute pipeline
            summary = self.execute_pipeline()

            # Check if successful
            if summary["status"] == "completed":
                improvement = summary["stage_results"].get("improve", {}).get("improvement", 0)
                logger.info(f"Cycle completed. Improvement: {improvement:.3f}")
            else:
                logger.error(f"Cycle failed: {summary.get('error')}")

            # Wait before next cycle
            if i < cycles - 1:
                logger.info(f"Waiting {interval_seconds} seconds before next cycle...")
                time.sleep(interval_seconds)

        logger.info("Continuous pipeline completed")

        # Generate overall summary
        overall_summary = self._generate_overall_summary()
        logger.info(f"Overall summary: {overall_summary}")

        return overall_summary

    def _generate_overall_summary(self) -> Dict[str, Any]:
        """Generate overall summary of all pipeline runs"""
        total_cycles = len(self.pipeline_history)
        successful_cycles = sum(1 for h in self.pipeline_history if h["status"] == "completed")

        if successful_cycles > 0:
            avg_duration = sum(h["total_duration"] for h in self.pipeline_history) / total_cycles
            avg_improvement = sum(
                h["stage_results"].get("improve", {}).get("improvement", 0)
                for h in self.pipeline_history if h["status"] == "completed"
            ) / successful_cycles
        else:
            avg_duration = 0
            avg_improvement = 0

        summary = {
            "total_cycles": total_cycles,
            "successful_cycles": successful_cycles,
            "failed_cycles": total_cycles - successful_cycles,
            "success_rate": successful_cycles / total_cycles if total_cycles > 0 else 0,
            "average_duration": avg_duration,
            "average_improvement": avg_improvement,
            "history": self.pipeline_history
        }

        return summary


class AsyncPipelineRunner:
    """
    Runs pipeline asynchronously in background
    """

    def __init__(self, pipeline: AutonomousPipeline):
        """
        Initialize async runner

        Args:
            pipeline: Pipeline to run
        """
        self.pipeline = pipeline
        self.thread = None
        self.is_running = False

    def start_async(self, cycles: int = 5, interval_seconds: int = 60):
        """
        Start pipeline asynchronously

        Args:
            cycles: Number of cycles
            interval_seconds: Interval between cycles
        """
        if self.is_running:
            logger.warning("Pipeline already running")
            return

        self.is_running = True
        self.thread = threading.Thread(
            target=self.pipeline.run_continuous_pipeline,
            args=(cycles, interval_seconds)
        )
        self.thread.start()

        logger.info("Async pipeline started")

    def stop(self):
        """Stop async pipeline"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Async pipeline stopped")

    def is_alive(self) -> bool:
        """Check if pipeline is running"""
        return self.thread and self.thread.is_alive()


if __name__ == "__main__":
    # Example usage
    pipeline = AutonomousPipeline()
    pipeline.setup_default_pipeline()

    # Run single pipeline execution
    context = {
        "collect_count": 5,
        "generate_count": 5,
        "data_type": "qa"
    }

    summary = pipeline.execute_pipeline(context)
    print(f"Pipeline summary: {summary}")

    # Run continuous pipeline
    # overall_summary = pipeline.run_continuous_pipeline(cycles=3, interval_seconds=30)
    # print(f"Overall summary: {overall_summary}")
