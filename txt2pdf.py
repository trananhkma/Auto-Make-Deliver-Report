# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


PAGE_SIZE = A4
LEFT = 2*cm
RIGHT = 2*cm
TOP = 2*cm
BOTTOM = 2*cm
AUTHOR = None
TITLE = None
FONT_SIZE = 10
LEADING = None
KERNING = 0
FONT = 'Courier'


def readfile(infile, nChars):
    with open(infile, 'r') as f:
        nbr = 0
        for l0 in f:
            l = l0.decode("utf-8")
            nbr += 1
            l = l[:-1] # remove trailing newspace \n character
            if len(l) > nChars:
                while len(l) > nChars:
                    yield l[:nChars]
                    l = l[nChars:]
            yield l


def newpage(c, font, fontsize, top, mleft, leading0, kerning):
    textobject = c.beginText()
    textobject.setFont(font, fontsize, leading=leading0)
    textobject.setTextOrigin(mleft, top)
    textobject.setCharSpace( kerning )
    return textobject


def pdf_create(c, data, outfile, font, fontsize, top, mleft, lpp, leading, kerning):
    p,l = 1, 0
    t = newpage(c, font, fontsize, top, mleft, leading, kerning)
    for line in data:
        t.textLine(line)
        l += 1
        if l == lpp:
            c.drawText(t)
            c.drawRightString(10*cm, 1*cm, str(p))
            c.showPage()
            l = 0
            p += 1
            t = newpage(c, font, fontsize, top, mleft, leading, kerning)
    if l > 0:
        c.drawText(t)
        c.drawRightString(10*cm, 1*cm, str(p))
    else:
        p -= 1
    c.save()


def get_outfile(infile):
    if '.' in infile:
        outfile = infile[:infile.rfind('.')] + '.pdf'
    else:
        outfile = infile + '.pdf'
    return outfile


def convert(infile):
    outfile = get_outfile(infile)
    c = canvas.Canvas(outfile, pagesize=PAGE_SIZE)
    if AUTHOR:
        c.setAuthor(AUTHOR)
    if TITLE:
        c.setTitle(TITLE)

    width = PAGE_SIZE[0] - LEFT - RIGHT
    w = c.stringWidth(".", fontName=FONT, fontSize=FONT_SIZE)
    nChars = int((width + KERNING) / (w + KERNING))
    top = PAGE_SIZE[1] - TOP - FONT_SIZE

    if LEADING:
        nLines = int((LEADING + PAGE_SIZE[1] - TOP - BOTTOM - FONT_SIZE) / (LEADING))
    else:
        nLines = int((1.2*FONT_SIZE + PAGE_SIZE[1] - TOP - BOTTOM - FONT_SIZE) / (1.2*FONT_SIZE))


    data = readfile(infile, nChars)
    pdf_create(c, data, outfile, FONT, FONT_SIZE, top, LEFT, nLines, LEADING, KERNING)
    return outfile