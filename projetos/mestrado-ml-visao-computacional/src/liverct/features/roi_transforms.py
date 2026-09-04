from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

import numpy as np
from PIL import Image, ImageDraw


RoiMode = Literal["full_image", "roi_crop_aproximada", "roi_mask_heuristica"]
MaskShape = Literal["ellipse", "rectangle"]


@dataclass(frozen=True)
class RoiBoxFractions:
    """
    Approximate ROI box expressed as fractions of image width and height.

    This is a technical heuristic for exploratory experiments. It is not a
    liver segmentation and must not be interpreted as a clinical mask.
    """

    center_x: float = 0.44
    center_y: float = 0.53
    width: float = 0.68
    height: float = 0.70

    def validate(self) -> None:
        """Validate fractional ROI parameters."""
        for name, value in [
            ("center_x", self.center_x),
            ("center_y", self.center_y),
            ("width", self.width),
            ("height", self.height),
        ]:
            if not 0.0 < float(value) <= 1.0:
                raise ValueError(f"{name} must be in (0, 1]. Received: {value}")

    def to_pixel_box(self, image_size: tuple[int, int]) -> tuple[int, int, int, int]:
        """Convert fractional ROI parameters to a PIL crop box."""
        self.validate()

        image_width, image_height = image_size
        roi_width = max(1, int(round(image_width * self.width)))
        roi_height = max(1, int(round(image_height * self.height)))

        center_x_px = int(round(image_width * self.center_x))
        center_y_px = int(round(image_height * self.center_y))

        left = center_x_px - roi_width // 2
        upper = center_y_px - roi_height // 2
        right = left + roi_width
        lower = upper + roi_height

        if left < 0:
            right -= left
            left = 0
        if upper < 0:
            lower -= upper
            upper = 0
        if right > image_width:
            left -= right - image_width
            right = image_width
        if lower > image_height:
            upper -= lower - image_height
            lower = image_height

        left = max(0, left)
        upper = max(0, upper)
        right = min(image_width, max(left + 1, right))
        lower = min(image_height, max(upper + 1, lower))

        return left, upper, right, lower


def ensure_grayscale(image: Image.Image) -> Image.Image:
    """Return a grayscale copy of an image."""
    return image.convert("L")


def full_image(image: Image.Image) -> Image.Image:
    """Return the full image without ROI restriction."""
    return ensure_grayscale(image)


def crop_approximate_liver_roi(
    image: Image.Image,
    roi_box: RoiBoxFractions | None = None,
) -> Image.Image:
    """
    Crop an approximate hepatic region using fixed fractional coordinates.

    The crop is intentionally simple and configurable. It is meant to test
    sensitivity to regions outside the approximate liver area, not to segment
    the liver.
    """
    roi = roi_box or RoiBoxFractions()
    gray = ensure_grayscale(image)
    return gray.crop(roi.to_pixel_box(gray.size))


def mask_approximate_liver_roi(
    image: Image.Image,
    roi_box: RoiBoxFractions | None = None,
    mask_shape: MaskShape = "ellipse",
    outside_value: int = 0,
) -> Image.Image:
    """
    Keep pixels inside an approximate ROI and set the outside area to a constant.

    This mask is geometric and heuristic. It does not represent a validated
    liver contour.
    """
    roi = roi_box or RoiBoxFractions()
    gray = ensure_grayscale(image)
    box = roi.to_pixel_box(gray.size)

    mask = Image.new("L", gray.size, 0)
    draw = ImageDraw.Draw(mask)

    if mask_shape == "ellipse":
        draw.ellipse(box, fill=255)
    elif mask_shape == "rectangle":
        draw.rectangle(box, fill=255)
    else:
        raise ValueError(f"Unsupported mask_shape: {mask_shape}")

    image_array = np.asarray(gray, dtype=np.uint8)
    mask_array = np.asarray(mask, dtype=np.uint8) > 0
    fill_value = int(np.clip(outside_value, 0, 255))
    masked = np.where(mask_array, image_array, fill_value).astype(np.uint8)

    return Image.fromarray(masked, mode="L")


@dataclass(frozen=True)
class RoiImageTransform:
    """Pickle-friendly callable used by PyTorch dataloaders."""

    mode: RoiMode
    roi_box: RoiBoxFractions = RoiBoxFractions()
    mask_shape: MaskShape = "ellipse"

    def __call__(self, image: Image.Image) -> Image.Image:
        if self.mode == "full_image":
            return full_image(image)
        if self.mode == "roi_crop_aproximada":
            return crop_approximate_liver_roi(image, roi_box=self.roi_box)
        if self.mode == "roi_mask_heuristica":
            return mask_approximate_liver_roi(
                image,
                roi_box=self.roi_box,
                mask_shape=self.mask_shape,
            )

        raise ValueError(f"Unsupported ROI mode: {self.mode}")


def build_roi_transform(
    mode: RoiMode,
    roi_box: RoiBoxFractions | None = None,
    mask_shape: MaskShape = "ellipse",
) -> Callable[[Image.Image], Image.Image]:
    """Build a PIL image transform for one ROI experiment mode."""
    roi = roi_box or RoiBoxFractions()
    return RoiImageTransform(mode=mode, roi_box=roi, mask_shape=mask_shape)


def describe_roi_mode(mode: RoiMode) -> str:
    """Return a short methodological description for an ROI mode."""
    descriptions = {
        "full_image": "Imagem inteira, equivalente ao baseline CNN 2D.",
        "roi_crop_aproximada": (
            "Recorte fixo e aproximado da regiao hepatica; heuristico e nao clinico."
        ),
        "roi_mask_heuristica": (
            "Mascara geometrica aproximada para reduzir fundo e fora da ROI; "
            "heuristica e nao clinica."
        ),
    }
    return descriptions[mode]
