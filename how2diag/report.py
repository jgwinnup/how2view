
#
#  Utilities for HTML page reporting
#

#
# Get POS tag superset from a list
#
import html


def getpossuperset(dictlist):

    superset = {}

    for d in dictlist:
        for k in d.keys():
            superset[k] = True

    return list(superset.keys())


def header(fh, title):

    fh.write('<HTML>\n')
    fh.write('<HEAD>\n')
    fh.write('<meta charset="utf-8"/>\n')
    floatboxcss(fh)
    fh.write('</HEAD>\n')
    fh.write(f'<TITLE>{title}</title>\n')
    fh.write('<BODY>\n')
    fh.write(f'<h1>{title}</h1>\n')


def footer(fh):

    fh.write('</BODY>\n')
    fh.write('</HTML>\n')


def posreport(fh, ref, t1, t2):

    allpos = getpossuperset([ref, t1, t2])

    fh.write('<table>\n')
    fh.write(f'<tr><th>POS</th><th>Ref</th><th>T1</th><th>T2</th></tr>\n')
    for t in allpos:
        fh.write(
            f'<tr><td>{t}</td><td>{ref.get(t, 0)}</td><td>{t1.get(t, 0)}</td><td>{t2.get(t, 0)}</td></tr>\n')
    fh.write('</table>\n')


def showsent(fh, toktup, label):

    words = [f'<td>{t[0]}</td>' for t in toktup]
    pos = [f'<td>{t[1]}</td>' for t in toktup]

    fh.write(f'<h2>{label}</h2>\n')
    fh.write('<table border="1">\n')
    fh.write(f'<tr>{" ".join(words)}</tr>\n')
    fh.write(f'<tr>{" ".join(pos)}</tr>\n')
    fh.write('</table>\n')


# def scoretable(fh, cond, t1bleu, t2bleu, t1lev, t2lev):
def scoretable(fh, stats):
    fh.write('<table border=1>\n')

    for k, v in stats.items():
        fh.write(f'<tr><td align="right">{k}</td><td>{html.escape(str(v))}</td></tr>\n')

    # fh.write(f'<tr><td>Cond:</td><td>{html.escape(cond)}</td></tr>\n')
    # fh.write(f'<tr><td>T1 Sent BLEU:</td><td>{t1bleu}</td></tr>\n')
    # fh.write(f'<tr><td>ref vs T1 Lev:</td><td>{t1lev}</td></tr>\n')
    # fh.write(f'<tr><td>T2 Sent BLEU:</td><td>{t2bleu}</td></tr>\n')
    # fh.write(f'<tr><td>ref vs T2 Lev:</td><td>{t2lev}</td></tr>\n')
    fh.write('</table>\n')


def floatboxcss(fh):

    css = """
<style>

table {
    border: 1px solid black;
}

.container {
  height: 80px;
  width: 330px;
  margin: auto;
}

button {
  float: right;
  margin: 1.3em 1.6em 0 0;
}

.closed {
  overflow-y: hidden;
}

.child {
  width: 50px;
  height: 30px;
  background-color: grey;
  display: inline-block;
  margin: 1em;
}
</style>
    """
    fh.write(css)