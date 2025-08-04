# import os
#
# import cv2
# import numpy as np
#
# # Maybe get rid of this?
# import pywinctl
# from pyautogui import screenshot
#
#
# class Region:
#
#     def __init__(self, left: int, top: int, width: int, height: int):
#         self.left = left
#         self.top = top
#         self.width = width
#         self.height = height
#
#     def is_empty(self):
#         return self.width == 0 and self.height == 0
#
#     def as_ltwh_tuple(self) -> tuple[int, int, int, int]:
#         return self.left, self.top, self.width, self.height
#
#     def as_ltrb_tuple(self) -> tuple[int, int, int, int]:
#         return self.left, self.top, self.left + self.width, self.top + self.height
#
#     def __str__(self):
#         return f"{self.left=}, {self.top=}, {self.width=}, {self.height=}"
#
#
# def take_screenshot(region: Region = None) -> np.ndarray:
#     if region is not None:
#         region = region.as_ltwh_tuple()
#
#     if os.name == "nt":
#         img = screenshot(allScreens=True, region=region)
#     else:
#         img = screenshot(region=region)
#
#     img = np.array(img)
#     img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
#     return img
#
#
# # Currently not working
# def calculate_frame_dimensions(img: np.ndarray) -> Region | None:
#     orange_lines_regions: list[Region] = []
#     orange_bar_hue = 38
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#
#     def match_hsv(hue: int, saturation: int, value: int) -> bool:
#         matched_hue = abs(orange_bar_hue - 2 * hue) <= 8
#         matched_saturation = saturation > 0.90 * 255
#         matched_value = value > 0.70 * 255
#         return matched_hue and matched_saturation and matched_value
#
#     for y in range(img.shape[0]):
#         if not any(
#             [
#                 match_hsv(*img[y, 1 * img.shape[1] // 4]),
#                 match_hsv(*img[y, 2 * img.shape[1] // 4]),
#                 match_hsv(*img[y, 3 * img.shape[1] // 4]),
#             ]
#         ):
#             continue
#         found_line = False
#         left = 0
#         for x in range(img.shape[1]):
#             matched = match_hsv(*img[y, x])
#             if not found_line and matched:
#                 found_line = True
#                 left = x
#
#             if found_line and not matched:
#                 break
#
#         orange_lines_regions.append(Region(left, y, x - left + 1, 1))
#
#     orange_lines_regions = [
#         region for region in orange_lines_regions if region.width > 50
#     ]
#
#     if len(orange_lines_regions) == 0:
#         return None
#     else:
#         left = min(orange_lines_regions, key=lambda x: x.left).left
#         top = min(orange_lines_regions, key=lambda x: x.top).top
#         right = max(
#             orange_lines_regions, key=lambda x: x.as_ltrb_tuple()[2]
#         ).as_ltrb_tuple()[2]
#         bot = max(
#             orange_lines_regions, key=lambda x: x.as_ltrb_tuple()[3]
#         ).as_ltrb_tuple()[3]
#         return Region(left, top, right - left, bot - top)
#
#
# win = pywinctl.getWindowsWithTitle("Weston Compositor - screen0")
# win = win[0]
#
# img = take_screenshot(Region(win.left, win.top, win.width, win.height))
#
#
# reg = calculate_frame_dimensions(img)
# print(reg)
#
#
# cv2.waitKey(0)
# cv2.destroyAllWindows()
