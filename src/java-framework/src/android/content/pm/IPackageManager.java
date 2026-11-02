package android.content.pm;

/** The package manager's binder surface (system-internal). */
public interface IPackageManager extends android.os.IInterface {
    IPackageInstaller getPackageInstaller();

    abstract class Stub extends android.os.Binder implements IPackageManager {
        public static final String DESCRIPTOR = "android.content.pm.IPackageManager";
        public static IPackageManager asInterface(android.os.IBinder b) {
            if (b == null) return null;
            android.os.IInterface local = b.queryLocalInterface(DESCRIPTOR);
            return local instanceof IPackageManager ? (IPackageManager) local : new Stub() {};
        }
        public android.os.IBinder asBinder() { return this; }
        public IPackageInstaller getPackageInstaller() { return new IPackageInstaller.Stub() {}; }
    }
}
