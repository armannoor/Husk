package android.content.pm;

/** The package installer's session service (system-internal). */
public interface IPackageInstaller extends android.os.IInterface {
    IPackageInstallerSession openSession(int sessionId);

    abstract class Stub extends android.os.Binder implements IPackageInstaller {
        public static final String DESCRIPTOR = "android.content.pm.IPackageInstaller";
        public static IPackageInstaller asInterface(android.os.IBinder b) {
            if (b == null) return null;
            android.os.IInterface local = b.queryLocalInterface(DESCRIPTOR);
            return local instanceof IPackageInstaller ? (IPackageInstaller) local : new Stub() {};
        }
        public android.os.IBinder asBinder() { return this; }
        public IPackageInstallerSession openSession(int sessionId) { return new IPackageInstallerSession.Stub() {}; }
    }
}
