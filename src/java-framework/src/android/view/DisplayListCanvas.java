package android.view;

import android.graphics.Bitmap;
import android.graphics.Canvas;

/**
 * The canvas RenderNode.start() hands out: an ordinary software canvas over the
 * node's bitmap. drawRenderNode() replays a child node's bitmap with its
 * transform, which is all the layer needs without a GPU renderer.
 */
public class DisplayListCanvas extends HardwareCanvas {
    private final RenderNode mNode;
    private boolean mRecording = true;

    DisplayListCanvas(RenderNode node, Bitmap bitmap) {
        super(bitmap);
        mNode = node;
    }

    public void drawRenderNode(RenderNode node) {
        if (node != null) node.drawInto(this, null);
    }

    void finishRecording() { mRecording = false; }
}
