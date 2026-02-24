"""
GPU Scheduler module.

Responsible for:
- Selecting best GPU node
- Dispatching detection jobs
"""

class GPUScheduler:
    def __init__(self):
        """
        Initialize GPU scheduler.
        """
        self.nodes = ["gpu-node-1", "gpu-node-2"]

    def select_best_node(self):
        """
        Select best available GPU node.
        Currently uses simple round-robin strategy.
        """
        # Simple example logic
        return self.nodes[0]

    def dispatch(self, node, job):
        """
        Dispatch job to selected GPU node.
        """
        print(f"Dispatching job {job} to {node}")

    def submit_detection_job(self, image, timestamp):
        """
        Submit detection job to GPU cluster.
        """
        node = self.select_best_node()

        job = {
            "type": "detection",
            "timestamp": timestamp,
            "image_present": image is not None
        }

        self.dispatch(node, job)