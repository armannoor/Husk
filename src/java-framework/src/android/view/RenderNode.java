package android.view;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Matrix;
import android.graphics.Outline;
import android.graphics.Paint;

/**
 * A display list: what a View records once and replays each frame. Husk has no
 * hardware renderer, so a node owns an off-screen bitmap; start() hands out a
 * canvas that draws into it and drawRenderNode() blits it with the node's
 * transform. That is enough for the androidx drawing helpers that use it.
 */
public class RenderNode {
    private final String mName;
    private final View mOwner;
    private Bitmap mBitmap;
    private int mWidth = 1, mHeight = 1;
    private int mLeft, mTop, mRight, mBottom;
    private float mAlpha = 1f, mTranslationX, mTranslationY, mElevation;
    private float mScaleX = 1f, mScaleY = 1f, mRotation, mRotationX, mRotationY;
    private float mPivotX, mPivotY, mCameraDistance;
    private int mAmbientShadowColor, mSpotShadowColor, mLayerType;
    private boolean mValid = true, mClipToBounds, mClipToOutline, mOverlapping = true;
    private Paint mLayerPaint;
    private Outline mOutline;

    RenderNode(String name, View owner) { mName = name; mOwner = owner; }

    public static RenderNode create(String name, View owner) { return new RenderNode(name, owner); }

    public DisplayListCanvas start(int width, int height) {
        width = Math.max(1, width); height = Math.max(1, height);
        if (mBitmap == null || mWidth != width || mHeight != height) {
            mBitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
            mWidth = width; mHeight = height;
        }
        return new DisplayListCanvas(this, mBitmap);
    }

    public void end(DisplayListCanvas canvas) { if (canvas != null) canvas.finishRecording(); }
    public void discardDisplayList() {}
    public void destroyDisplayListData() { mBitmap = null; }
    public boolean isValid() { return mValid; }

    Bitmap bitmap() { return mBitmap; }

    void drawInto(Canvas canvas, Paint paint) {
        if (mBitmap == null || !mValid) return;
        canvas.save();
        canvas.translate(mTranslationX, mTranslationY);
        if (mRotation != 0) canvas.rotate(mRotation, mPivotX, mPivotY);
        if (mScaleX != 1f || mScaleY != 1f) canvas.scale(mScaleX, mScaleY, mPivotX, mPivotY);
        if (paint == null) paint = mLayerPaint;
        if (paint == null) paint = new Paint();
        paint.setAlpha((int) (255 * Math.max(0f, Math.min(1f, mAlpha))));
        canvas.drawBitmap(mBitmap, 0, 0, paint);
        canvas.restore();
    }

    public void getMatrix(Matrix out) {
        out.reset();
        out.postTranslate(mTranslationX, mTranslationY);
        if (mRotation != 0) out.postRotate(mRotation, mPivotX, mPivotY);
        if (mScaleX != 1f || mScaleY != 1f) out.postScale(mScaleX, mScaleY, mPivotX, mPivotY);
    }

    /** The inverse of getMatrix(): what turns a touch in the parent into a touch in this node. */
    public void getInverseMatrix(Matrix out) {
        getMatrix(out);
        Matrix inv = new Matrix();
        if (out.invert(inv)) out.set(inv);
    }

    public int getWidth() { return mWidth; }
    public int getHeight() { return mHeight; }
    public int getLeft() { return mLeft; }
    public int getTop() { return mTop; }
    public int getRight() { return mRight; }
    public int getBottom() { return mBottom; }

    public boolean setLeftTopRightBottom(int left, int top, int right, int bottom) {
        mLeft = left; mTop = top; mRight = right; mBottom = bottom;
        return true;
    }
    public boolean offsetLeftAndRight(int offset) { mLeft += offset; mRight += offset; return true; }
    public boolean offsetTopAndBottom(int offset) { mTop += offset; mBottom += offset; return true; }
    public boolean setPosition(int left, int top, int right, int bottom) { return setLeftTopRightBottom(left, top, right, bottom); }

    public float getAlpha() { return mAlpha; }
    public boolean setAlpha(float alpha) { mAlpha = alpha; return true; }
    public float getTranslationX() { return mTranslationX; }
    public boolean setTranslationX(float x) { mTranslationX = x; return true; }
    public float getTranslationY() { return mTranslationY; }
    public boolean setTranslationY(float y) { mTranslationY = y; return true; }
    public float getElevation() { return mElevation; }
    public boolean setElevation(float e) { mElevation = e; return true; }
    public float getScaleX() { return mScaleX; }
    public boolean setScaleX(float x) { mScaleX = x; return true; }
    public float getScaleY() { return mScaleY; }
    public boolean setScaleY(float y) { mScaleY = y; return true; }
    public float getRotation() { return mRotation; }
    public boolean setRotation(float r) { mRotation = r; return true; }
    public float getRotationX() { return mRotationX; }
    public boolean setRotationX(float r) { mRotationX = r; return true; }
    public float getRotationY() { return mRotationY; }
    public boolean setRotationY(float r) { mRotationY = r; return true; }
    public float getPivotX() { return mPivotX; }
    public boolean setPivotX(float x) { mPivotX = x; return true; }
    public float getPivotY() { return mPivotY; }
    public boolean setPivotY(float y) { mPivotY = y; return true; }
    public float getCameraDistance() { return mCameraDistance; }
    public boolean setCameraDistance(float d) { mCameraDistance = d; return true; }
    public int getAmbientShadowColor() { return mAmbientShadowColor; }
    public boolean setAmbientShadowColor(int c) { mAmbientShadowColor = c; return true; }
    public int getSpotShadowColor() { return mSpotShadowColor; }
    public boolean setSpotShadowColor(int c) { mSpotShadowColor = c; return true; }
    public boolean getClipToOutline() { return mClipToOutline; }
    public boolean setClipToOutline(boolean b) { mClipToOutline = b; return true; }
    public boolean setClipToBounds(boolean b) { mClipToBounds = b; return true; }
    public boolean hasOverlappingRendering() { return mOverlapping; }
    public boolean setHasOverlappingRendering(boolean b) { mOverlapping = b; return true; }
    public boolean setLayerType(int type) { mLayerType = type; return true; }
    public boolean setLayerPaint(Paint p) { mLayerPaint = p; return true; }
    public boolean setOutline(Outline o) { mOutline = o; return true; }
}
