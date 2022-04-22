import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.widgets import Slider, Button, RadioButtons
import numpy as np

# permet de générer un affichage
def display(data, lines, display_range=0.6):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    lineVol = getLinesVolume(lines, 0.002)

    c = np.concatenate((np.full(len(data), 'w'), np.full(len(lineVol), 'r')))
    ec = np.concatenate((np.full(len(data), 'k'), np.full(len(lineVol), 'r')))
    d = np.concatenate((np.asarray(data), np.asarray(lineVol)))

    ax.add_collection3d(Poly3DCollection(d, facecolors=c, edgecolors=ec, linewidths=0.1, alpha=0.7, zsort='average'))

    ax.auto_scale_xyz([-display_range, display_range], [-display_range, display_range], [-display_range, display_range])
    ax.set_box_aspect((1, 1, 1))
    plt.show()
    plt.savefig("slice_stl_proj.png")

# permet de construire des lignes sous forme de 3 face en xyz,
# afin d'afficher une ligne correctement dans matplotlib
def getLinesVolume(lines, off):


    vol = []
    for l in lines:
        A = l[0]
        B = l[1]

        A1 = [A[0], A[1], A[2] + off]
        A2 = [A[0] + off, A[1], A[2]]
        A3 = [A[0], A[1], A[2] - off]
        A4 = [A[0] - off, A[1], A[2]]
        A5 = [A[0], A[1] + off, A[2]]
        A6 = [A[0], A[1] - off, A[2]]

        B1 = [B[0], B[1], B[2] + off]
        B2 = [B[0] + off, B[1], B[2]]
        B3 = [B[0], B[1], B[2] - off]
        B4 = [B[0] - off, B[1], B[2]]
        B5 = [B[0], B[1] + off, B[2]]
        B6 = [B[0], B[1] - off, B[2]]

        vol.append([A1, A3, B3])
        vol.append([A1, B3, B1])

        vol.append([A4, A2, B2])
        vol.append([A4, B4, B2])

        vol.append([A6, A5, B5])
        vol.append([A6, B6, B5])

    return vol

##### fonctions pratiques de la librairie numpy-stl ######

mydtype = numpy.dtype([
    ('normals', numpy.float32, (3,)),
    ('vectors', numpy.float32, (3, 3)),
    ('attr', numpy.uint16, (1,)),
])

BUFFER_SIZE = 80

def b(s, encoding='ascii', errors='replace'):  # pragma: no cover
    if isinstance(s, str):
        return bytes(s, encoding, errors)
    else:
        return s


def _ascii_reader(fh, header):
    if b'\n' in header:
        recoverable = [True]
    else:
        recoverable = [False]
        header += b(fh.read(BUFFER_SIZE))

    lines = b(header).split(b('\n'))

    def get(prefix=''):
        prefix = b(prefix).lower()

        if lines:
            raw_line = lines.pop(0)
        else:
            raise RuntimeError(recoverable[0], 'Unable to find more lines')

        if not lines:
            recoverable[0] = False

            # Read more lines and make sure we prepend any old data
            lines[:] = b(fh.read(BUFFER_SIZE)).split(b('\n'))
            raw_line += lines.pop(0)

        raw_line = raw_line.strip()
        line = raw_line.lower()
        if line == b(''):
            return get(prefix)

        if prefix:
            if line.startswith(prefix):
                values = line.replace(prefix, b(''), 1).strip().split()
            elif line.startswith(b('endsolid')):
                # go back to the beginning of new solid part
                size_unprocessedlines = sum(len(l) + 1 for l in lines) - 1
                if size_unprocessedlines > 0:
                    position = fh.tell()
                    fh.seek(position - size_unprocessedlines)
                raise StopIteration()
            else:
                raise RuntimeError(recoverable[0],
                                   '%r should start with %r' % (line,
                                                                prefix))

            if len(values) == 3:
                return [float(v) for v in values]
            else:  # pragma: no cover
                raise RuntimeError(recoverable[0],
                                   'Incorrect value %r' % line)
        else:
            return b(raw_line)

    line = get()
    if not lines:
        raise RuntimeError(recoverable[0],
                           'No lines found, impossible to read')

    # Yield the name
    yield line[5:].strip()

    while True:
        # Read from the header lines first, until that point we can recover
        # and go to the binary option. After that we cannot due to
        # unseekable files such as sys.stdin
        #
        # Numpy doesn't support any non-file types so wrapping with a
        # buffer and/or StringIO does not work.
        try:
            normals = get('facet normal')
            assert get() == b('outer loop')
            v0 = get('vertex')
            v1 = get('vertex')
            v2 = get('vertex')
            assert get() == b('endloop')
            assert get() == b('endfacet')
            attrs = 0
            yield (normals, (v0, v1, v2), attrs)
        except AssertionError as e:  # pragma: no cover
            raise RuntimeError(recoverable[0], e)
        except StopIteration:
            return


def _load_ascii(fh, header):
    # The speedups module is covered by travis but it can't be tested in
    # all environments, this makes coverage checks easier
    iterator = _ascii_reader(fh, header)
    name = next(iterator)
    return name, numpy.fromiter(iterator, dtype=mydtype)


def loadStlFile(fileName):
    with open(fileName, 'rb') as fh:
        header = fh.read(80)
        name, data = _load_ascii(fh, header)
        return data['vectors'].tolist()
