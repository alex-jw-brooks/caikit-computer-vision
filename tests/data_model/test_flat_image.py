"""Test decoded image data model.
"""
# Third Party
import numpy as np
import pytest

# First Party
from caikit.interfaces.vision import data_model as caikit_dm

# Local
from caikit_computer_vision.data_model import FlatChannel, FlatImage

width = 10
height = 10
decoded_im = np.random.randint(low=0, high=256, dtype=np.uint8, size=(width, height, 3))
flat_arr = decoded_im.reshape((3, width * height))

# Tests for FlatChannel
def test_flat_channel_cannot_be_ommitted():
    """Ensure that if we don't pass anything, we raise TypeError."""
    with pytest.raises(TypeError):
        FlatChannel()


# For now, we just check value bounds; it might be a good idea to check
# dtype etc as well to ensure we are not passing floats, but for now we omit
# it for performance reasons.
@pytest.mark.parametrize(
    "sad_channel",
    [
        [
            300,
        ],
        [
            -100,
        ],
    ],
)
def test_flat_channel_must_be_uint8(sad_channel):
    """Ensure if we get values outside of uint8's range, we raise ValueError."""
    with pytest.raises(ValueError):
        FlatChannel(sad_channel)


@pytest.mark.parametrize("happy_channel", [[], [10, 20, 30, 40, 50]])
def test_flat_channel_creation_and_serialization(happy_channel):
    """For valid values, ensure we can build a FlatChannel and serialize/deserialize it."""
    ch = FlatChannel(happy_channel)
    assert isinstance(ch, FlatChannel)

    proto_flat_channel = ch.to_proto()
    rebuilt_channel = FlatChannel.from_proto(proto_flat_channel)
    assert isinstance(rebuilt_channel, FlatChannel)
    assert rebuilt_channel.values == happy_channel


# Tests for FlatImage
def test_flat_image_creation_and_serialization():
    """Ensure we can build and serialize flat an image from flat channels."""
    flat_channels = [FlatChannel(ch) for ch in flat_arr.tolist()]

    flat_im = FlatImage(flat_channels=flat_channels, image_shape=flat_arr.shape)

    proto_flat_im = flat_im.to_proto()
    rebuilt_flat_im = FlatImage.from_proto(proto_flat_im)
    assert isinstance(rebuilt_flat_im, FlatImage)


def test_flat_image_uneven_channels():
    """Ensure that we cannot build an image with uneven channels."""
    flat_channels = [FlatChannel([1, 3, 4]), FlatChannel([3, 1])]
    with pytest.raises(ValueError):
        flat_im = FlatImage(flat_channels=flat_channels, image_shape=flat_arr.shape)


def test_flat_image_wrong_shape():
    """Ensure that we cannot build an image with a wrong shape."""
    flat_channels = [FlatChannel([1, 3, 4]), FlatChannel([3, 1, 3])]
    with pytest.raises(ValueError):
        flat_im = FlatImage(
            flat_channels=flat_channels,
            image_shape=(
                1,
                1,
            ),
        )


def test_flat_image_matches_dm_np_arr():
    """Ensure that a flat np arr"""
    # Essentially. we want to make sure if we build an image from a np arr,
    # and do the same from a flat image, we get the same result we bring it back
    decoded_im = np.random.randint(low=0, high=256, dtype=np.uint8, size=(50, 100, 3))
    # Build the Image DM, then convert to a numpy array
    recon_from_img = caikit_dm.Image(decoded_im).as_numpy()

    # Now use the same decoded image to build a flattened arr
    recon_from_flat_img = FlatImage.from_numpy(decoded_im).to_numpy()

    # Both reconstructions should be numpy arrays of the same shape
    assert isinstance(recon_from_img, np.ndarray)
    assert isinstance(recon_from_flat_img, np.ndarray)
    assert recon_from_img.shape == recon_from_flat_img.shape

    # And also, we should get the same resulting array
    assert (recon_from_img == recon_from_flat_img).all()
