"""
Phase 2 Frame Processing Test - Real Camera Frame Extraction and Quality Assessment
Following FACEGUARD_V2_STRATEGIC_IMPLEMENTATION_GUIDE.md - Zero Placeholder Code
"""
import asyncio
import time
import sys
import os
import psutil
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import get_settings
from services.camera_manager import CameraManager
from domain.models import FrameQuality

class FrameProcessingTester:
    """Test frame processing capabilities with real camera"""
    
    def __init__(self):
        self.settings = get_settings()
        self.camera_manager = None
        self.test_results = {}
        self.start_memory = None
        
    async def initialize(self):
        """Initialize camera manager for testing"""
        print("🔧 Initializing Camera Manager for Frame Processing Test...")
        self.camera_manager = CameraManager(self.settings)
        await self.camera_manager.initialize()
        
        # Record initial memory usage
        process = psutil.Process()
        self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"📊 Initial memory usage: {self.start_memory:.2f} MB")
        
    async def test_basic_frame_capture(self):
        """Test basic frame capture functionality"""
        print("\n🎥 Testing Basic Frame Capture...")
        
        try:
            # Get camera info
            cameras = self.camera_manager.get_all_cameras_info()
            if not cameras:
                raise Exception("No cameras configured")
            
            camera_id = cameras[0].camera_id
            print(f"   Testing with camera: {camera_id}")
            
            # Connect camera if not connected
            if cameras[0].status.value != "connected":
                print("   Connecting camera...")
                success = await self.camera_manager.connect_camera(camera_id)
                if not success:
                    raise Exception("Failed to connect camera")
            
            # Capture single frame
            print("   Capturing test frame...")
            start_time = time.time()
            frame_data = await self.camera_manager.get_frame(camera_id, timeout=10.0)
            capture_time = (time.time() - start_time) * 1000  # ms
            
            if frame_data is None:
                raise Exception("Failed to capture frame")
                
            frame, metadata = frame_data
            
            print(f"   ✅ Frame captured successfully!")
            print(f"      Frame size: {metadata.width}x{metadata.height}x{metadata.channels}")
            print(f"      File size: {metadata.file_size} bytes")
            print(f"      Capture time: {capture_time:.2f}ms")
            print(f"      Frame ID: {metadata.frame_id}")
            
            self.test_results['basic_capture'] = {
                'success': True,
                'capture_time_ms': capture_time,
                'frame_size': (metadata.width, metadata.height, metadata.channels),
                'file_size_bytes': metadata.file_size
            }
            
            return True
            
        except Exception as e:
            print(f"   ❌ Basic frame capture failed: {e}")
            self.test_results['basic_capture'] = {'success': False, 'error': str(e)}
            return False
    
    async def test_frame_quality_assessment(self):
        """Test frame quality assessment with real frames"""
        print("\n🔍 Testing Frame Quality Assessment...")
        
        try:
            cameras = self.camera_manager.get_all_cameras_info()
            camera_id = cameras[0].camera_id
            
            # Capture multiple frames for quality testing
            quality_scores = []
            quality_grades = []
            
            print("   Capturing and analyzing 5 frames...")
            for i in range(5):
                frame_data = await self.camera_manager.get_frame(camera_id, timeout=5.0)
                if frame_data is None:
                    continue
                    
                frame, metadata = frame_data
                
                # Get quality assessment
                if hasattr(metadata, 'quality_score') and metadata.quality_score is not None:
                    quality_scores.append(metadata.quality_score)
                    quality_grades.append(metadata.quality_grade.value)
                    print(f"      Frame {i+1}: Quality score {metadata.quality_score:.3f} ({metadata.quality_grade.value})")
                else:
                    # Quality assessment not in metadata, test directly
                    camera = self.camera_manager.cameras[camera_id]
                    quality_score, quality_grade = camera.assess_frame_quality(frame)
                    quality_scores.append(quality_score)
                    quality_grades.append(quality_grade.value)
                    print(f"      Frame {i+1}: Quality score {quality_score:.3f} ({quality_grade.value})")
            
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                print(f"   ✅ Quality assessment working!")
                print(f"      Average quality score: {avg_quality:.3f}")
                print(f"      Quality grades: {set(quality_grades)}")
                
                self.test_results['quality_assessment'] = {
                    'success': True,
                    'avg_quality_score': avg_quality,
                    'quality_grades': list(set(quality_grades)),
                    'frames_analyzed': len(quality_scores)
                }
                return True
            else:
                raise Exception("No frames captured for quality assessment")
                
        except Exception as e:
            print(f"   ❌ Quality assessment failed: {e}")
            self.test_results['quality_assessment'] = {'success': False, 'error': str(e)}
            return False
    
    async def test_stream_processing(self):
        """Test continuous stream processing"""
        print("\n🔄 Testing Stream Processing...")
        
        try:
            cameras = self.camera_manager.get_all_cameras_info()
            camera_id = cameras[0].camera_id
            
            # Start stream processing
            print("   Starting stream processing...")
            success = await self.camera_manager.start_stream(camera_id)
            if not success:
                raise Exception("Failed to start stream")
            
            # Monitor stream for 10 seconds
            print("   Monitoring stream for 10 seconds...")
            start_time = time.time()
            frames_processed = 0
            
            while time.time() - start_time < 10:
                frame_data = await self.camera_manager.get_frame(camera_id, timeout=2.0)
                if frame_data is not None:
                    frames_processed += 1
                    frame, metadata = frame_data
                    print(f"      Frame {frames_processed}: {metadata.width}x{metadata.height} "
                          f"(Quality: {getattr(metadata, 'quality_score', 'N/A')})")
                await asyncio.sleep(0.5)  # Process at 2 FPS
            
            # Stop stream
            await self.camera_manager.stop_stream(camera_id)
            
            processing_time = time.time() - start_time
            fps = frames_processed / processing_time
            
            print(f"   ✅ Stream processing successful!")
            print(f"      Frames processed: {frames_processed}")
            print(f"      Processing time: {processing_time:.2f}s")
            print(f"      Effective FPS: {fps:.2f}")
            
            self.test_results['stream_processing'] = {
                'success': True,
                'frames_processed': frames_processed,
                'processing_time': processing_time,
                'effective_fps': fps
            }
            
            return True
            
        except Exception as e:
            print(f"   ❌ Stream processing failed: {e}")
            self.test_results['stream_processing'] = {'success': False, 'error': str(e)}
            return False
    
    async def test_memory_stability(self):
        """Test memory usage during frame processing"""
        print("\n💾 Testing Memory Stability...")
        
        try:
            cameras = self.camera_manager.get_all_cameras_info()
            camera_id = cameras[0].camera_id
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process frames for 30 seconds
            print("   Processing frames for 30 seconds to check memory stability...")
            start_time = time.time()
            frames_processed = 0
            memory_readings = []
            
            # Start stream
            await self.camera_manager.start_stream(camera_id)
            
            while time.time() - start_time < 30:
                frame_data = await self.camera_manager.get_frame(camera_id, timeout=2.0)
                if frame_data is not None:
                    frames_processed += 1
                
                # Record memory every 5 seconds
                if frames_processed % 10 == 0:  # Every ~5 seconds at 2 FPS
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_readings.append(current_memory)
                    print(f"      Memory usage: {current_memory:.2f} MB (frames: {frames_processed})")
                
                await asyncio.sleep(0.5)
            
            # Stop stream
            await self.camera_manager.stop_stream(camera_id)
            
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_growth = final_memory - initial_memory
            
            print(f"   ✅ Memory stability test complete!")
            print(f"      Initial memory: {initial_memory:.2f} MB")
            print(f"      Final memory: {final_memory:.2f} MB")
            print(f"      Memory growth: {memory_growth:.2f} MB")
            print(f"      Frames processed: {frames_processed}")
            
            # Memory growth should be reasonable (< 50MB for 30 seconds)
            memory_stable = memory_growth < 50
            
            self.test_results['memory_stability'] = {
                'success': memory_stable,
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_growth_mb': memory_growth,
                'frames_processed': frames_processed,
                'memory_stable': memory_stable
            }
            
            return memory_stable
            
        except Exception as e:
            print(f"   ❌ Memory stability test failed: {e}")
            self.test_results['memory_stability'] = {'success': False, 'error': str(e)}
            return False
    
    async def test_buffer_management(self):
        """Test frame buffer management"""
        print("\n🗃️ Testing Buffer Management...")
        
        try:
            cameras = self.camera_manager.get_all_cameras_info()
            camera_id = cameras[0].camera_id
            
            # Start stream processing
            await self.camera_manager.start_stream(camera_id)
            
            # Fill buffer rapidly
            print("   Testing buffer fill behavior...")
            start_time = time.time()
            successful_frames = 0
            buffer_full_count = 0
            
            # Try to process frames rapidly for 5 seconds
            while time.time() - start_time < 5:
                frame_data = await self.camera_manager.get_frame(camera_id, timeout=0.1)
                if frame_data is not None:
                    successful_frames += 1
                else:
                    buffer_full_count += 1
                
                # Don't sleep - stress test the buffer
            
            await self.camera_manager.stop_stream(camera_id)
            
            print(f"   ✅ Buffer management test complete!")
            print(f"      Successful frames: {successful_frames}")
            print(f"      Buffer timeouts: {buffer_full_count}")
            
            # Buffer should handle reasonable load
            buffer_working = successful_frames > 0
            
            self.test_results['buffer_management'] = {
                'success': buffer_working,
                'successful_frames': successful_frames,
                'buffer_timeouts': buffer_full_count,
                'buffer_working': buffer_working
            }
            
            return buffer_working
            
        except Exception as e:
            print(f"   ❌ Buffer management test failed: {e}")
            self.test_results['buffer_management'] = {'success': False, 'error': str(e)}
            return False
    
    async def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📋 PHASE 2 FRAME PROCESSING TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('success', False))
        
        print(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n💾 Memory Usage:")
        process = psutil.Process()
        current_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = current_memory - self.start_memory
        print(f"   Initial: {self.start_memory:.2f} MB")
        print(f"   Current: {current_memory:.2f} MB") 
        print(f"   Growth: {memory_growth:.2f} MB")
        
        print(f"\n🔧 Test Details:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if not result.get('success', False) and 'error' in result:
                print(f"      Error: {result['error']}")
        
        # Phase 2 Quality Gate Assessment
        print(f"\n🎯 PHASE 2 QUALITY GATE ASSESSMENT:")
        
        critical_tests = ['basic_capture', 'quality_assessment', 'stream_processing', 'memory_stability']
        critical_passed = sum(1 for test in critical_tests if self.test_results.get(test, {}).get('success', False))
        
        if critical_passed == len(critical_tests):
            print("   🎉 PHASE 2 QUALITY GATE: PASSED")
            print("   ✅ Frame extraction working")
            print("   ✅ Quality validation functional") 
            print("   ✅ Memory stable during operation")
            print("   ✅ Stream processing operational")
            print("   🚀 Ready for PHASE 3: Recognition Integration")
        else:
            print("   ⚠️  PHASE 2 QUALITY GATE: NEEDS WORK")
            print(f"   {critical_passed}/{len(critical_tests)} critical tests passed")
        
        return passed_tests == total_tests

async def main():
    """Run Phase 2 frame processing tests"""
    print("🧪 PHASE 2 FRAME PROCESSING VALIDATION")
    print("Following FACEGUARD_V2_STRATEGIC_IMPLEMENTATION_GUIDE.md")
    print("Zero Placeholder Code - Real Camera Operations Only")
    print("="*60)
    
    tester = FrameProcessingTester()
    
    try:
        # Initialize
        await tester.initialize()
        
        # Run all tests
        tests = [
            tester.test_basic_frame_capture(),
            tester.test_frame_quality_assessment(),
            tester.test_stream_processing(),
            tester.test_memory_stability(),
            tester.test_buffer_management()
        ]
        
        # Execute tests sequentially 
        for test in tests:
            await test
        
        # Generate final report
        success = await tester.generate_report()
        
        return success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if tester.camera_manager:
            await tester.camera_manager.shutdown()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)