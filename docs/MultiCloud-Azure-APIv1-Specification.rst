.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. Copyright (c) 2018 Amdocs

=====================================
MultiCloud Azure APIv1 Specification
=====================================

The is the specification for MultiCloud Azure API version v1.

Note: "MultiCloud Azure API Specification V1" refers to the specification for MultiCloud Azure API version v0.

API Catalog
===========

1. **Scope**
^^^^^^^^^^^^

The scope of the present document is to describe the MutliCloud NorthBound API
specification.

2. **Registration Management**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

2.1. **Update VIM Info**
-------------------------

===================== =================================================================================
IF Definition          Description
===================== =================================================================================
URI                    msb.onap.org:80/api/multicloud-azure/v1/{cloud-owner}/{cloud-region-id}/registry
Operation              POST
Direction              ESR-> MULTICLOUD
Description            Register a VIM instance to AAI
===================== =================================================================================

2.1.1. **Request**
>>>>>>>>>>>>>>>>>>>

NA

2.1.2. **Response**
>>>>>>>>>>>>>>>>>>>>

NA

202: accept

400: failed

2.2. **Unregistry VIM**
------------------------

===================== ========================================================================
IF Definition          Description
===================== ========================================================================
URI                    msb.onap.org:80/api/multicloud-azure/v1/{cloud-owner}/{cloud-region-id}
Operation              DELETE
Direction              ESR-> MULTICLOUD
Description            Unregister a VIM instance from AAI
===================== ========================================================================


2.2.1. **Request**
>>>>>>>>>>>>>>>>>>>

NA

2.2.2. **Response**
>>>>>>>>>>>>>>>>>>>>

NA

204: No content found

400: failed



2. **infrastructure workload LCM**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

2.1. **Instantiate infrastructure workload**
---------------------------------------------

===================== =======================================================================================
IF Definition          Description
===================== =======================================================================================
URI                    msb.onap.org:80/api/multicloud-azure/v1/{cloud-owner}/{cloud-region-id}/infra_workload
Operation              POST
Direction              SO-> MULTICLOUD
Description            Instantiate infrastructure workload
===================== =======================================================================================

2.1.1. **Request**
>>>>>>>>>>>>>>>>>>>

================ ========= ============ ======== ==============================================================================
Parameter        Qualifier Cardinality  Content    Description
================ ========= ============ ======== ==============================================================================
generic-vnf-id       O         1        string          generif VNF ID to search AAI object
vf-module-id         O         1        string          vf module id  to search AAI object
oof_directives       O         1        Object          oof directives to update template_data
sdnc_directives      O         1        Object          sdnc directives to update template_data
template_type        M         1        string          template type with which the MultiCloud plugin inteprates template_data
                                                            "heat",etc.
template_data        M         1        Object          workload template data to instantiate workload onto VIM/Cloud instance
================ ========= ============ ======== ==============================================================================

::

  {
     "generic-vnf-id":"vnf-id-111111",
     "vf-module-id":"vf-module-id-2222222",
     "oof_directives":{},
     "sdnc_directives":{
		"temp_key":"temp_value"
	 },
     "template_type":"heat",
     "template_data":{{
         "files":{  },
         "disable_rollback":true,
         "parameters":{
            "flavor":"m1.heat"
         },
         "stack_name":"teststack",
         "template":{},
         "timeout_mins":60
     }
  }

2.1.2. **Response**
>>>>>>>>>>>>>>>>>>>>

================== ========= ============ ======== ==============================================================================
Parameter          Qualifier Cardinality  Content    Description
================== ========= ============ ======== ==============================================================================
template_type          M         1        string          template type with which the MultiCloud plugin inteprates template_data
                                                            "heat",etc.
workload_id            M         1        string          The ID of infrastructure workload resource
================== ========= ============ ======== ==============================================================================


201: Created

400: Bad Request

401: Unauthorized

409: Conflict

::

    {
        "template_type":"heat",
        "workload_id": "1234567890abcd"

    }


2.2. **Query infrastructure workload**
---------------------------------------

===================== =====================================================================================================
IF Definition          Description
===================== =====================================================================================================
URI                    msb.onap.org:80/api/multicloud-azure/v1/{cloud-owner}/{cloud-region-id}/infra_workload/{workload-id}
Operation              GET
Direction              SO-> MULTICLOUD
Description            Query the status of the infrastructure workload
===================== =====================================================================================================


2.2.1. **Request**
>>>>>>>>>>>>>>>>>>>

NA

2.2.2. **Response**
>>>>>>>>>>>>>>>>>>>>

================== ========= ============ ======== ==============================================================================
Parameter          Qualifier Cardinality  Content    Description
================== ========= ============ ======== ==============================================================================
template_type          M         1        string          template type with which the MultiCloud plugin inteprates template_data
                                                            "heat",etc.
workload_id            M         1        string          The ID of infrastructure workload resource
workload_status        M         1        string          Status of infrastructure workload:
                                                              CREATE_IN_PROGRESS, CREATE_COMPLETE, CREATE_FAILED
================== ========= ============ ======== ==============================================================================


200: OK

400: Bad Request

401: Unauthorized

404: Not Found

500: Internal Server Error

::

    {
        "template_type":"heat",
        "workload_id": "1234567890abcd",
        "workload_status":"CREATE_IN_PROGRESS"
    }
