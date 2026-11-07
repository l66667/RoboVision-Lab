# -*- coding: utf-8 -*-
"""Static-image adaptation of the MIT pick-and-place rotation detector.

Original: https://github.com/SasiriChathurika/rotation-angle-detection-for-pick-place-robots
Author: Sasiri Chathurika
License: MIT (see LICENSE in this directory)

Changes: static images, explicit keypoints/descriptors, inlier diagnostics,
angle normalization, no webcam.
"""

import argparse
import os
import sys

import cv2
import numpy as np


def load_gray(path):
    data = np.fromfile(path, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(path)
    return image


def detect_rotation(reference, scene, ratio=0.6, min_good=20, ransac=5.0):
    sift = cv2.SIFT_create()
    kp_ref, desc_ref = sift.detectAndCompute(reference, None)
    kp_scene, desc_scene = sift.detectAndCompute(scene, None)
    if desc_ref is None or desc_scene is None:
        return None, None, None

    flann = cv2.FlannBasedMatcher(dict(algorithm=0, trees=5), {})
    knn = flann.knnMatch(desc_ref, desc_scene, k=2)
    good = [m for m, n in knn if m.distance < ratio * n.distance]
    if len(good) <= min_good:
        return None, good, None

    src = np.float32([kp_ref[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kp_scene[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    homography, mask = cv2.findHomography(dst, src, cv2.RANSAC, ransac)
    if homography is None:
        return None, good, None

    angle = float(np.degrees(np.arctan2(homography[1, 0], homography[0, 0])))
    # Normalize to (-90, 90]; a 180-degree flip is ambiguous for a flat part.
    if angle > 90:
        angle -= 180
    elif angle <= -90:
        angle += 180
    matches = cv2.drawMatches(reference, kp_ref, scene, kp_scene, good[:80], None, flags=2)
    return angle, good, (matches, int(mask.sum()), homography)


def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", nargs="?", default=os.path.join(root, "data", "samples", "github_card_ref.jpg"))
    parser.add_argument("scene", nargs="?", default=os.path.join(root, "data", "samples", "github_card_scene.jpg"))
    parser.add_argument("output", nargs="?", default=os.path.join(root, "projects", "github-rotation", "result.jpg"))
    args = parser.parse_args()

    reference = load_gray(args.reference)
    scene = load_gray(args.scene)
    angle, good, extra = detect_rotation(reference, scene)
    if angle is None:
        print("not enough matches")
        return 1
    matches, inliers, homography = extra
    print("good matches:", len(good))
    print("inliers:", inliers)
    print("rotation: %.2f deg" % angle)
    cv2.imwrite(args.output, matches)
    print("saved:", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
