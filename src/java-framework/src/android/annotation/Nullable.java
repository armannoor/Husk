package android.annotation;

/** A parameter/field/return value may be null (compile-time documentation; no runtime effect). */
@java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.CLASS)
@java.lang.annotation.Target({java.lang.annotation.ElementType.METHOD, java.lang.annotation.ElementType.PARAMETER,
        java.lang.annotation.ElementType.FIELD, java.lang.annotation.ElementType.LOCAL_VARIABLE,
        java.lang.annotation.ElementType.ANNOTATION_TYPE, java.lang.annotation.ElementType.PACKAGE,
        java.lang.annotation.ElementType.TYPE_USE})
public @interface Nullable {}
