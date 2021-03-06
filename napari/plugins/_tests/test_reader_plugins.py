import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np
from napari.utils import io

from napari.plugins.io import read_data_with_plugins


def test_builtin_reader_plugin(viewer_factory):
    """Test the builtin reader plugin reads a temporary file."""
    from napari.plugins import plugin_manager

    plugin_manager.hooks.napari_get_reader.bring_to_front(['builtins'])

    with NamedTemporaryFile(suffix='.tif', delete=False) as tmp:
        data = np.random.rand(20, 20)
        io.imsave(tmp.name, data)
        tmp.seek(0)
        layer_data = read_data_with_plugins(tmp.name)

        assert isinstance(layer_data, list)
        assert len(layer_data) == 1
        assert isinstance(layer_data[0], tuple)
        assert np.allclose(data, layer_data[0][0])

        view, viewer = viewer_factory()
        viewer.open(tmp.name)

        assert np.allclose(viewer.layers[0].data, data)


def test_builtin_reader_plugin_csv(viewer_factory, tmpdir):
    """Test the builtin reader plugin reads a temporary file."""
    from napari.plugins import plugin_manager

    plugin_manager.hooks.napari_get_reader.bring_to_front(['builtins'])

    tmp = os.path.join(tmpdir, 'test.csv')
    column_names = ['index', 'axis-0', 'axis-1']
    table = np.random.random((5, 3))
    data = table[:, 1:]
    # Write csv file
    io.write_csv(tmp, table, column_names=column_names)
    layer_data = read_data_with_plugins(tmp)

    assert isinstance(layer_data, list)
    assert len(layer_data) == 1
    assert isinstance(layer_data[0], tuple)
    assert layer_data[0][2] == 'points'
    assert np.allclose(data, layer_data[0][0])

    view, viewer = viewer_factory()
    viewer.open(tmp)

    assert np.allclose(viewer.layers[0].data, data)


def test_builtin_reader_plugin_stacks(viewer_factory):
    """Test the builtin reader plugin reads multiple files as a stack."""
    from napari.plugins import plugin_manager

    plugin_manager.hooks.napari_get_reader.bring_to_front(['builtins'])

    data = np.random.rand(5, 20, 20)
    tmps = []
    for plane in data:
        tmp = NamedTemporaryFile(suffix='.tif', delete=False)
        io.imsave(tmp.name, plane)
        tmp.seek(0)
        tmps.append(tmp)

    _, viewer = viewer_factory()
    # open should take both strings and Path object, so we make one of the
    # pathnames a Path object
    names = [tmp.name for tmp in tmps]
    names[0] = Path(names[0])
    viewer.open(names, stack=True)
    assert np.allclose(viewer.layers[0].data, data)
    for tmp in tmps:
        tmp.close()
        os.unlink(tmp.name)
