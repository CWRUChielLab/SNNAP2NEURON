#include <stdio.h>
#include "hocdec.h"
extern int nrnmpi_myid;
extern int nrn_nobanner_;

extern void _a_mechs_reg(void);
extern void _b_mechs_reg(void);
extern void _c_mechs_reg(void);

void modl_reg(){
  if (!nrn_nobanner_) if (nrnmpi_myid < 1) {
    fprintf(stderr, "Additional mechanisms from files\n");

    fprintf(stderr," a_mechs.mod");
    fprintf(stderr," b_mechs.mod");
    fprintf(stderr," c_mechs.mod");
    fprintf(stderr, "\n");
  }
  _a_mechs_reg();
  _b_mechs_reg();
  _c_mechs_reg();
}
