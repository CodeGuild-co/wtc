using System;
using System.Drawing;
using System.Windows.Forms;

class Program: Form
{
    public const decimal
        ax = 0,
        ay = 700,
        bx = 700,
        by = 700,
        cx = 350,
        cy = 0;
    public decimal
        dx = ax,
        dy = ay;
    public Random r;
    public Image img;
    public Graphics g;

    public static void Main()
    {
        Application.Run(new Program());
    }

    public Program()
    {
        r = new Random();
        this.img = new Bitmap(700, 700);
        this.g = Graphics.FromImage(this.img);
        this.ClientSize = new Size(700,700);
        this.Paint += DoPaint;
	this.DoubleBuffered = true;
	this.Invalidate();
    }

    public void DoPaint(object sender, PaintEventArgs e)
    {
        int tgt = r.Next(3);
        decimal tgtx = 0, tgty = 0;
        switch (tgt)
        {
            case 0:
                tgtx = ax;
                tgty = ay;
                break;

            case 1:
                tgtx = bx;
                tgty = by;
                break;

            case 2:
                tgtx = cx;
                tgty = cy;
                break;
        }

        dx = (dx + tgtx)/2;
        dy = (dy + tgty)/2;
	Console.WriteLine("{0}, {1} ({2}, {3})", dx, dy, (int)dx, (int)dy);
        g.FillRectangle(Brushes.Red, (int)dx, (int)dy, 1, 1);
        e.Graphics.DrawImage(img, 0, 0);
        this.Invalidate();
    }
}
