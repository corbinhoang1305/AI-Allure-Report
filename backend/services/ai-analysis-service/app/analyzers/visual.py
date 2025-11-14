"""
Visual Analysis Module
Compares screenshots from test failures to detect UI issues
"""
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import io
import base64

from shared.utils import logger


class VisualAnalyzer:
    """Analyzer for visual/UI test failures"""
    
    def __init__(self, similarity_threshold: float = 0.95):
        """
        Initialize visual analyzer
        
        Args:
            similarity_threshold: Threshold for considering images similar (0.0 to 1.0)
        """
        self.similarity_threshold = similarity_threshold
    
    def compare_screenshots(
        self,
        baseline_image: bytes,
        current_image: bytes,
        test_name: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Compare two screenshots and detect visual differences
        
        Args:
            baseline_image: Baseline (passing) screenshot as bytes
            current_image: Current (failed) screenshot as bytes
            test_name: Name of the test
            
        Returns:
            Analysis results with differences highlighted
        """
        try:
            # Load images
            img_baseline = self._load_image(baseline_image)
            img_current = self._load_image(current_image)
            
            # Resize images to same size if needed
            if img_baseline.shape != img_current.shape:
                img_current = cv2.resize(img_current, (img_baseline.shape[1], img_baseline.shape[0]))
            
            # Calculate similarity
            similarity_score = self._calculate_similarity(img_baseline, img_current)
            
            # Detect differences
            differences = self._detect_differences(img_baseline, img_current)
            
            # Generate diff image
            diff_image = self._create_diff_image(img_baseline, img_current, differences)
            
            # Analyze difference types
            analysis = self._analyze_differences(differences, img_baseline.shape)
            
            result = {
                "test_name": test_name,
                "similarity_score": similarity_score,
                "has_differences": similarity_score < self.similarity_threshold,
                "difference_percentage": (1 - similarity_score) * 100,
                "differences_detected": len(differences),
                "analysis": analysis,
                "diff_image_base64": self._encode_image(diff_image) if diff_image is not None else None
            }
            
            logger.info(f"Visual analysis completed for {test_name}: {similarity_score:.2%} similar")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in visual analysis: {str(e)}")
            return {
                "test_name": test_name,
                "error": str(e),
                "has_differences": False
            }
    
    def _load_image(self, image_data: bytes) -> np.ndarray:
        """Load image from bytes"""
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    
    def _calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate similarity between two images using SSIM"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Calculate Mean Squared Error
        mse = np.mean((gray1 - gray2) ** 2)
        
        if mse == 0:
            return 1.0
        
        # Calculate PSNR (Peak Signal-to-Noise Ratio)
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        
        # Normalize to 0-1 range
        similarity = min(psnr / 50, 1.0)  # 50 dB is considered very good
        
        return similarity
    
    def _detect_differences(
        self,
        img1: np.ndarray,
        img2: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Detect specific areas of difference"""
        # Calculate absolute difference
        diff = cv2.absdiff(img1, img2)
        
        # Convert to grayscale
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Threshold to binary
        _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        differences = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter out small noise
                x, y, w, h = cv2.boundingRect(contour)
                differences.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "area": int(area)
                })
        
        return differences
    
    def _create_diff_image(
        self,
        img1: np.ndarray,
        img2: np.ndarray,
        differences: List[Dict[str, Any]]
    ) -> Optional[np.ndarray]:
        """Create a visual diff image with differences highlighted"""
        try:
            # Start with current image
            diff_img = img2.copy()
            
            # Draw rectangles around differences
            for diff in differences:
                x, y, w, h = diff["x"], diff["y"], diff["width"], diff["height"]
                # Draw red rectangle
                cv2.rectangle(diff_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            return diff_img
            
        except Exception as e:
            logger.error(f"Error creating diff image: {str(e)}")
            return None
    
    def _analyze_differences(
        self,
        differences: List[Dict[str, Any]],
        image_shape: Tuple[int, int, int]
    ) -> Dict[str, Any]:
        """Analyze the types and severity of differences"""
        if not differences:
            return {
                "summary": "No significant visual differences detected",
                "severity": "none"
            }
        
        total_area = image_shape[0] * image_shape[1]
        diff_area = sum(d["area"] for d in differences)
        coverage = (diff_area / total_area) * 100
        
        # Classify differences by size
        small_diffs = [d for d in differences if d["area"] < 1000]
        medium_diffs = [d for d in differences if 1000 <= d["area"] < 10000]
        large_diffs = [d for d in differences if d["area"] >= 10000]
        
        # Determine severity
        if coverage > 20 or len(large_diffs) > 0:
            severity = "critical"
            summary = "Major layout changes or missing elements detected"
        elif coverage > 5 or len(medium_diffs) > 2:
            severity = "high"
            summary = "Significant visual differences detected"
        elif len(small_diffs) > 5:
            severity = "medium"
            summary = "Multiple small visual differences detected"
        else:
            severity = "low"
            summary = "Minor visual differences detected"
        
        return {
            "summary": summary,
            "severity": severity,
            "coverage_percentage": round(coverage, 2),
            "difference_count": {
                "small": len(small_diffs),
                "medium": len(medium_diffs),
                "large": len(large_diffs)
            },
            "recommendations": self._generate_visual_recommendations(severity, differences)
        }
    
    def _generate_visual_recommendations(
        self,
        severity: str,
        differences: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on visual analysis"""
        recommendations = []
        
        if severity == "critical":
            recommendations.append("Investigate immediately - major UI changes detected")
            recommendations.append("Verify if changes are intentional or bug-related")
        elif severity == "high":
            recommendations.append("Review UI changes - significant differences found")
        
        if len(differences) > 10:
            recommendations.append("Multiple differences detected - consider full page review")
        
        large_diffs = [d for d in differences if d["area"] >= 10000]
        if large_diffs:
            recommendations.append("Large elements affected - possible layout break")
        
        return recommendations
    
    def _encode_image(self, img: np.ndarray) -> str:
        """Encode image to base64 string"""
        try:
            _, buffer = cv2.imencode('.png', img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            return img_base64
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            return ""
    
    def batch_compare(
        self,
        comparisons: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Compare multiple screenshot pairs in batch
        
        Args:
            comparisons: List of dicts with baseline_image, current_image, test_name
            
        Returns:
            List of comparison results
        """
        results = []
        
        for comparison in comparisons:
            result = self.compare_screenshots(
                baseline_image=comparison["baseline_image"],
                current_image=comparison["current_image"],
                test_name=comparison.get("test_name", "Unknown")
            )
            results.append(result)
        
        return results

