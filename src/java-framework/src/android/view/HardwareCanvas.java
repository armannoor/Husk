package android.view;

import android.graphics.Bitmap;
import android.graphics.Canvas;

/**
 * The hidden hardware-canvas base class. Husk has no GPU canvas, so this is a
 * plain software Canvas; RenderNode's recording canvas extends it.
 */
public class HardwareCanvas extends Canvas {
    public HardwareCanvas() { super(); }
    public HardwareCanvas(Bitmap bitmap) { super(bitmap); }
}
