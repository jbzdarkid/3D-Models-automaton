"""
Deals with image processing. This file is the bottleneck of the process, and
is thus using numpy for efficiency. As a result, it is not very easy to read.
"""
from PIL.Image import Resampling, fromarray, new
from numpy import array, dstack, inner, maximum, uint8, where

class ImageProcessor():
  """
  A class to handle all the imageprocessing done on the screenshots.
  Deals with blending (finding transparency), cropping, and stitching.
  """
  def __init__(self, y_rotations, x_rotations):
    self.target_dimension = 280
    self.target_size = 512 * 1024 # 512 KB
    self.cropping = {'left': [], 'top': [], 'right': [], 'bottom': []}
    self.images = []
    self.y_rotations = y_rotations
    self.x_rotations = 2*x_rotations+1 # Total vertical rotations

  def find_minimum_bounds(self, white_image, black_image):
    """
    Finds the extrema of the black pixels of the first black image,
    in order to find the limits of the HLMV viewport.
    We do this by sampling 3 lines in each direction (horizontal / vertical)
    """
    white_arr = array(white_image, dtype=int)
    black_arr = array(black_image, dtype=int)

    horizontal_samples = [
      len(black_arr[:, 0, 0]) * 1 // 4,
      len(black_arr[:, 0, 0]) * 2 // 4,
      len(black_arr[:, 0, 0]) * 3 // 4,
    ]

    # This returns a tuple of coordinates ([x0, x1, x2, x3, x4, ...], [y0, y1, y2, y3, y4, ...])
    # which are all black on the black_image and all white on the white_image
    h_empty_pixels = where(
      (white_arr[horizontal_samples, :, :] == [255, 255, 255])
      &
      (black_arr[horizontal_samples, :, :] == [0, 0, 0])
    )

    vertical_samples = [
      len(black_arr[0, :, 0]) * 1 // 4,
      len(black_arr[0, :, 0]) * 2 // 4,
      len(black_arr[0, :, 0]) * 3 // 4,
    ]

    # This returns a tuple of coordinates ([x0, x1, x2, x3, x4, ...], [y0, y1, y2, y3, y4, ...])
    # which are all black on the black_image and all white on the white_image
    v_empty_pixels = where(
      (white_arr[:, vertical_samples, :].sum(axis=2) == 255*3)
      &
      (black_arr[:, vertical_samples, :].sum(axis=2) == 0)
    )

    return (
      h_empty_pixels[1].min(), # Left
      v_empty_pixels[0].min(), # Top
      h_empty_pixels[1].max(), # Right
      v_empty_pixels[0].max(), # Bottom
    )

  def blend(self, white_image, black_image):
    """
    Blends two RGB images on white/black backgrounds into a transparent RGBA image.
    Then, finds the closest-cropped lines that are all white.
    Uses numpy because traversing python arrays is very slow.
    """

    # This needs to be dtype=int to prevent overflow/underflow, even though the underlying values are 0-255.
    white_arr = array(white_image, dtype=int)
    black_arr = array(black_image, dtype=int)

    # First, average the color of each pixel between the black and white frames.
    average_color = (white_arr + black_arr) / 2

    # Then, compute the delta in luminescence between the black and white images.
    # We are computing the percieved luminescence using an inner product.
    # https://en.wikipedia.org/wiki/Luma_(video)#Use_of_relative_luminance
    lum_delta = inner((white_arr - black_arr), [.299, .587, .114])
    # We define 'transparency' as the difference in luminescence between black and white.
    # If an item is fully opaque, it will be exactly the same on both white and black backgrounds. (255 - (37 - 37) = 255)
    # If an item is fully transparent, it will be white on a white background, and black on a black background. (255 - (255 - 0) = 0)
    # In rare cases (due to aliasing), the black image may be brighter than the white one. We raise those values to 0 to avoid errors.
    alpha = 255 - maximum(lum_delta, 0)

    # Calculate crop lines by looking for all-white && all-black pixels, i.e. places where the luma is zero.
    # np.any() will return 'True' for any rows which contain nonzero integers (because zero is Falsy).
    # Then, we use nonzero() to get the only indices which are 'True', which are the rows with content.
    # (nonzero returns a tuple for some reason, so we also have to [0] it.)
    horizontal = alpha.any(axis=0).nonzero()[0]
    vertical = alpha.any(axis=1).nonzero()[0]

    self.cropping['left'].append(horizontal[0])
    self.cropping['top'].append(vertical[0])
    self.cropping['right'].append(horizontal[-1])
    self.cropping['bottom'].append(vertical[-1])

    # Merge the colors and the alpha mask to create the final image.
    blended_arr = dstack((
      average_color[:, :, 0],
      average_color[:, :, 1],
      average_color[:, :, 2],
      alpha,
      ))

    # PIL expects all pixels to be uint8 (0-255).
    blended_image = fromarray(blended_arr.astype(uint8), mode='RGBA')
    blended_image = blended_image.crop((
        horizontal[0],
        vertical[0],
        horizontal[-1],
        vertical[-1]
        ))
    self.images.append(blended_image)

  def stitch(self):
    """
    Crops the images to a shared size, then pastes them together.
    Prompts for login and uploads to the wiki when done.
    """
    # Determining crop bounds
    min_cropping = (
        min(self.cropping['left']),
        min(self.cropping['top']),
        max(self.cropping['right']),
        max(self.cropping['bottom'])
    )
    print('Min cropping: ' + str(min_cropping))
    max_frame_size = (
        min_cropping[2] - min_cropping[0],
        min_cropping[3] - min_cropping[1]
        )
    print('Max frame size: ' + str(max_frame_size))
    target_ratio = self.target_dimension / max(max_frame_size)
    print(f'Target scaling ratio: {target_ratio:f}')
    max_frame_size = (
        int(target_ratio * max_frame_size[0]),
        int(target_ratio * max_frame_size[1])
        )
    print('Scaled max frame size: ' + str(max_frame_size))

    # Pasting together
    full_image = new(mode='RGBA', color=(255, 255, 255, 255), size=((
        (max_frame_size[0]+1)*self.y_rotations*self.x_rotations,
        max_frame_size[1]
    )))
    curr_offset = 0
    offset_map = []
    for i, image in enumerate(self.images):
      image = image.resize((
          int(image.width*target_ratio),
          int(image.height*target_ratio),
          ), Resampling.LANCZOS)
      left_crop = int(target_ratio*(self.cropping['left'][i]-min_cropping[0]))
      top_crop = int(target_ratio*(self.cropping['top'][i]-min_cropping[1]))
      full_image.paste(image, (curr_offset, top_crop), image)
      # Offset map adds 1 manually for some reason
      offset_map += [curr_offset-i, image.height, left_crop]
      # Increase by 1 each time to add a 1px gap
      curr_offset += image.width+1
    full_image = full_image.crop((
        0,
        0,
        curr_offset,
        max_frame_size[1],
    ))

    full_offset_map = ','.join((
      str(curr_offset),
      str(max_frame_size[0]),
      str(max_frame_size[1]),
      str(self.x_rotations),
      *[str(o) for o in offset_map]
    ))

    return (full_image, full_offset_map)
