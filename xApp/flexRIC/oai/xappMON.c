/*
 * * Funcionalidades:
 * - Identificação completa dos nós (MCC/MNC separados).
 * - Lista todos os SMs suportados com OID e Versão.
 * - Deep Dive automático para KPM (Métricas) e RC (Ações/Parâmetros Recursivos).
 * - Compatível com FlexRIC v02.03.
 */

#include "../../../../src/xApp/e42_xapp_api.h"
#include "../../../../src/util/alg_ds/alg/defer.h"
#include "../../../../src/util/time_now_us.h"
#include "../../../../src/util/alg_ds/ds/lock_guard/lock_guard.h"
#include "../../../../src/util/ngran_types.h"

// Includes dos Service Models (Caminhos validados v02.03)
#include "../../../../src/sm/rc_sm/ie/rc_data_ie.h" 
#include "../../../../src/sm/kpm_sm/kpm_sm_v02.03/ie/kpm_data_ie.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <signal.h>
#include <pthread.h>
#include <assert.h>

static pthread_mutex_t mtx;

// --- HELPER: Traduzir OID para Nome Legível ---
const char* get_sm_name(const char* oid, size_t len) {
    if (len == 0 || oid == NULL) return "Unknown SM OID";
    
    // KPM
    if (strstr(oid, "1.3.6.1.4.1.53148.1.2.2.2")) return "E2SM-KPM v2.03/v3.00";
    if (strstr(oid, "1.3.6.1.4.1.53148.1.2.2.1")) return "E2SM-KPM v2.01";
    
    // RC
    if (strstr(oid, "1.3.6.1.4.1.53148.1.1.2.3")) return "E2SM-RC v1.03";
    
    // Custom FlexRIC SMs
    if (strstr(oid, "1.3.6.1.4.1.53148.1.1.2.100")) return "E2SM-MAC";
    if (strstr(oid, "1.3.6.1.4.1.53148.1.1.2.101")) return "E2SM-RLC";
    if (strstr(oid, "1.3.6.1.4.1.53148.1.1.2.102")) return "E2SM-PDCP";
    if (strstr(oid, "1.3.6.1.4.1.53148.1.1.2.103")) return "E2SM-SLICE";
    if (strstr(oid, "1.3.6.1.4.1.53148.1.1.2.104")) return "E2SM-TC";
    if (strstr(oid, "1.3.6.1.4.1.53148.1.1.2.105")) return "E2SM-GTP";

    return "Unknown/Proprietary SM";
}

// =================================================================================
// SEÇÃO: E2SM-RC (Deep Dive Recursivo)
// =================================================================================

// Helper Recursivo para definições de parâmetros RC
void print_ran_param_def_recursive(ran_param_def_t* def, int level) {
    if (def == NULL) return;

    int type_id = (int)def->type;
    
    // 0=List, 1=Structure (Baseado no seu header ran_param_def.h)
    if (type_id == 0 || type_id == 1) { 
        
        // Acessa a union (lst ou strct têm a mesma estrutura interna ran_param_type_t)
        ran_param_type_t* container = (type_id == 0) ? def->lst : def->strct;
        
        if(container == NULL) return;

        printf(" [%s with %lu items]:\n", (type_id == 0) ? "List" : "Structure", (unsigned long)container->sz_ran_param);

        for (size_t i = 0; i < container->sz_ran_param; i++) {
            ran_param_lst_struct_t *item = &container->ran_param[i];
            
            // Indentação manual
            for(int k=0; k<=level; k++) printf("    ");
            
            printf("-> Item ID: %lu | Name: %.*s", 
                   (unsigned long)item->ran_param_id, 
                   (int)item->ran_param_name.len, item->ran_param_name.buf);

            if (item->ran_param_def != NULL) {
                print_ran_param_def_recursive(item->ran_param_def, level + 1);
            } else {
                printf("\n");
            }
        }
    } else {
        // Tipos primitivos
        printf(" [Type: ");
        switch (type_id) {
            case 1: printf("Integer]"); break;
            case 2: printf("Enumerated]"); break;
            case 3: printf("Boolean]"); break;
            case 4: printf("Bit String]"); break;
            case 5: printf("Octet String]"); break;
            case 6: printf("Printable String]"); break;
            default: printf("ID %d]", type_id); break;
        }
        printf("\n");
    }
}

void print_rc_details(e2sm_rc_func_def_t* rc) {
    printf("    \033[1;36m[+] DEEP DIVE: E2SM-RC Capabilities\033[0m\n"); // Ciano

    // 1. Report Styles
    if (rc->report != NULL) {
        printf("        -> Report Styles: %lu\n", (unsigned long)rc->report->sz_seq_report_sty);
        for (size_t i = 0; i < rc->report->sz_seq_report_sty; i++) {
            seq_report_sty_t *style = &rc->report->seq_report_sty[i];
            printf("           [%ld] Style_Type: %lu | Style_Name: %.*s\n", 
                   i+1, (unsigned long)style->report_type, (int)style->name.len, style->name.buf);
            
            if(style->sz_seq_ran_param > 0){
                for(size_t j=0; j < style->sz_seq_ran_param; j++){
                    // Cast para seq_ran_param_3_t (v02.03)
                    seq_ran_param_3_t *rp = (seq_ran_param_3_t *)&style->ran_param[j];
                    printf("               - Param ID: %lu | Name: %.*s", (unsigned long)rp->id, (int)rp->name.len, rp->name.buf);
                    
                    if(rp->def != NULL) print_ran_param_def_recursive(rp->def, 3);
                    else printf("\n");
                }
            }
        }
    }

    // 2. Control Styles
    if (rc->ctrl != NULL) {
        printf("        -> Control Styles: %lu\n", (unsigned long)rc->ctrl->sz_seq_ctrl_style);
        for (size_t i = 0; i < rc->ctrl->sz_seq_ctrl_style; i++) {
            seq_ctrl_style_t *style = &rc->ctrl->seq_ctrl_style[i];
            printf("           [%ld] Style_Type: %lu | Style_Name: %.*s\n", 
                   i+1, (unsigned long)style->style_type, (int)style->name.len, style->name.buf);

            // Ações de Controle
            if (style->sz_seq_ctrl_act > 0) {
                for(size_t k=0; k < style->sz_seq_ctrl_act; k++) {
                    seq_ctrl_act_2_t *act = &style->seq_ctrl_act[k];
                    printf("               > Action ID: %lu | Name: %.*s\n", 
                           (unsigned long)act->id, (int)act->name.len, act->name.buf);

                    // Parâmetros da Ação (Recursivo)
                    if (act->sz_seq_assoc_ran_param > 0) {
                        for(size_t m=0; m < act->sz_seq_assoc_ran_param; m++) {
                            seq_ran_param_3_t *cp = &act->assoc_ran_param[m];
                            printf("                   >> Param ID: %lu | Name: %.*s", 
                                   (unsigned long)cp->id, (int)cp->name.len, cp->name.buf);
                            
                            if(cp->def != NULL) print_ran_param_def_recursive(cp->def, 5);
                            else printf("\n");
                        }
                    }
                }
            }
        }
    }
    printf("\n");
}

// =================================================================================
// SEÇÃO: E2SM-KPM (Deep Dive Métricas)
// =================================================================================

void print_kpm_details(kpm_ran_function_def_t* kpm) {
    printf("    \033[1;32m[+] DEEP DIVE: E2SM-KPM Capabilities\033[0m\n"); // Verde

    if (kpm->sz_ric_report_style_list > 0) {
        printf("        -> Report Styles: %lu\n", (unsigned long)kpm->sz_ric_report_style_list);
        
        for (size_t i = 0; i < kpm->sz_ric_report_style_list; i++) {
            ric_report_style_item_t *style = &kpm->ric_report_style_list[i];
            
            printf("           [%ld] Style_Type: %lu | Style_Name: %.*s\n", 
                   i+1, 
                   (unsigned long)style->report_style_type,
                   (int)style->report_style_name.len, style->report_style_name.buf);
            
            // Lista de Métricas (meas_info_for_action_lst)
            if (style->meas_info_for_action_lst_len > 0) {
                printf("               [Measurements List]:\n");
                for(size_t k=0; k < style->meas_info_for_action_lst_len; k++) {
                    meas_info_for_action_lst_t *meas = &style->meas_info_for_action_lst[k];
                    printf("               - %.*s\n", (int)meas->name.len, meas->name.buf);
                }
            }
        }
    } else {
        printf("        -> No KPM Styles found.\n");
    }
    printf("\n");
}

// =================================================================================
// MAIN UNIFICADA
// =================================================================================

int main(int argc, char* argv[])
{
  fr_args_t args = init_fr_args(argc, argv);
  init_xapp_api(&args);
  sleep(1);

  e2_node_arr_xapp_t nodes = e2_nodes_xapp_api();
  defer({ free_e2_node_arr_xapp(&nodes); });

  printf("\n======================================================\n");
  printf("   Connected Nodes: %d\n", nodes.len);
  printf("======================================================\n");

  pthread_mutexattr_t attr = {0};
  pthread_mutex_init(&mtx, &attr);

  for (int i = 0; i < nodes.len; i++) {
    e2_node_connected_xapp_t* n = &nodes.n[i];
    
    // --- 1. HW INFO (Identificação do Nó) ---
    const char* node_type_str = "Unknown";
    if (n->id.type == ngran_gNB) node_type_str = "gNB (Monolithic)";
    else if (n->id.type == ngran_gNB_CU) node_type_str = "gNB-CU";
    else if (n->id.type == ngran_gNB_DU) node_type_str = "gNB-DU";
    else if (n->id.type == ngran_eNB) node_type_str = "eNB (LTE)";

    printf("\n------------------------------------------------------\n");
    printf("[NODE %d] Analysis\n", i);
    // MCC e MNC separados
    printf("    Type: %s | MCC: %d, MNC: %d\n", node_type_str, n->id.plmn.mcc, n->id.plmn.mnc);
    
    if(n->id.nb_id.nb_id > 0) printf("    Global ID: %d\n", n->id.nb_id.nb_id);
    
    printf("    Supported RAN Functions: %ld\n", n->len_rf);
    printf("------------------------------------------------------\n");

    // --- 2. LISTA GERAL DE SERVICE MODELS (HW Style) ---
    printf("    [+] Service Model List:\n");
    for (size_t j = 0; j < n->len_rf; j++) {
        sm_ran_function_t *rf = &n->rf[j];
        const char* sm_name = get_sm_name((char*)rf->oid.buf, rf->oid.len);
        
        printf("        -> ranFunction-Name: %s\n", sm_name);
        printf("           ranFunctionID: %d | ranFunctionRevision: %d | ranFunctionOID: %.*s\n", 
               rf->id, rf->rev, (int)rf->oid.len, (char*)rf->oid.buf);
    }
    printf("\n");

    // --- 3. DEEP DIVE (Detalhes Específicos) ---
    for (size_t j = 0; j < n->len_rf; j++) {
        sm_ran_function_t *rf = &n->rf[j];

        // Se for KPM, chama a função detalhada
        if (rf->defn.type == KPM_RAN_FUNC_DEF_E) {
            print_kpm_details(&rf->defn.kpm);
        }
        // Se for RC, chama a função detalhada (recursiva)
        else if (rf->defn.type == RC_RAN_FUNC_DEF_E) {
            print_rc_details(&rf->defn.rc);
        }
    }
  }

  printf("\n[INFO] Audit Complete. The xApp will remain active to maintain connection.\n");
  printf("[INFO] Press Ctrl+C to exit.\n");

  while (try_stop_xapp_api() == false) usleep(1000000);

  return 0;
}
