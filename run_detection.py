from core.detection import Detector

if __name__ == "__main__":
    image_path = "LANDSAT00000001.jpg"  # change this to your image path

    detector = Detector()
    results = detector.detect(image_path)

    print("\nDetections:")
    for r in results:
        print(r)
