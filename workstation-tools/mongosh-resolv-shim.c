/*
 * Compatibility shim for running the glibc-linked mongosh binary on Alpine's
 * musl libc through gcompat.
 *
 * gcompat 1.1.0 provides most of the glibc ABI but not the two double-underscore
 * resolver aliases that mongosh's prebuilt linux-x64 binary imports at load
 * time:
 *   __res_nsearch, __dn_expand.
 * Without them the gcompat loader fails with
 *   "Error relocating ...: __res_nsearch: symbol not found".
 * This shim exports both names and delegates to musl's res_search / dn_expand.
 * The /usr/local/bin/mongosh wrapper LD_PRELOADs it before exec'ing the real
 * /opt/mongosh/bin/mongosh binary.
 */
extern int res_search(const char *dname, int rclass, int type,
                      unsigned char *answer, int anslen);
extern int dn_expand(const unsigned char *msg, const unsigned char *eom,
                     const unsigned char *src, char *dst, int dstsiz);

int __res_nsearch(void *state, const char *dname, int rclass, int type,
                  unsigned char *answer, int anslen)
{
    (void)state;
    return res_search(dname, rclass, type, answer, anslen);
}

int __dn_expand(const unsigned char *msg, const unsigned char *eom,
                const unsigned char *src, char *dst, int dstsiz)
{
    return dn_expand(msg, eom, src, dst, dstsiz);
}
