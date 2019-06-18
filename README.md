# helper to work with config for affirmed networks

## objective

to have possibility export config in python objects and 
as a result modify it inside python script.

## supported object

not any object recognized, done it especially to limit manual errors.
At this moment supported and interpreted as objects: SR, RG, MI, BP, QF.
   
## about config syntax

- syntax based on format delimiters (like in python or yaml)
- "!" - comment, if first symbol in line or as delimiter of list or object

### part of config which can be interpret as object 

```
service-construct service-rule SR_mmkelwflaw_2020
 admin-state                                 enabled
 priority                                    100
 service-data-flow-id                        2020
 http-rule-group                             HRG_msisdnffef3424
 tcp-filter                                  all
 service-activation                          always-on
 install-default-bearer-packet-filters-on-ue disabled
 packet-filter PF__01
 !
 packet-filter PF__02
 !
 packet-filter PF__03
 !
 packet-filter PF__04
 !
 packet-filter PF__05
 !
!
```

## Example

for interactive it better to use it inside ipython

### load config from files

```ipython
                                                                                                                             
In [1]: import ANconf as an                                                                                                  

# merge multiple file in one 'conf' object                                                                                                                             
In [2]: conf = an.load(["Test_ANparser\\test_file_2.txt", "Test_ANparser\\test_RGs.txt", "Test_ANparser\\test_BPs.txt"])     

# show what inside python object                                                                                                                             
In [3]: an.show(conf)                                                                                                        
service-construct service-rule SR_5001_GX-2535410                                                                            
 admin-state                                 enabled                                                                         
 priority                                    150                                                                             
 service-data-flow-id                        252001                                                                          
 tcp-filter                                  all                                                                             
 service-activation                          external-activation                                                             
 pcc-rule-name                               25510                                                                           
 install-default-bearer-packet-filters-on-ue disabled                                                                        
 packet-filter PF__25001_01                                                                                                  
 !                                                                                                                           
 packet-filter PF__25001_02                                                                                                  
 !                                                                                                                           
 packet-filter PF__25001_03   
 ..........
                                                                                                
```

### split config on dict-s

```ipython
# now we can create dict of ojects based by name of object, for easy manipulation 
In [6]: Bp = {o.name: o for o in conf.config["services charging billing-plan"]}

In [7]: Rg = {o.name: o for o in conf.config["services charging rating-group"]}

In [8]: Sr = {o.name: o for o in conf.config["service-construct service-rule"]}

In [9]: Sr.keys()
Out[9]: dict_keys(['SR_5001_GX-2535410', 'SR__5052', 'SR_wefwqfewf25001_GX-25X0'])

In [10]: an.show(Sr['SR_5001_GX-2535410'])
service-construct service-rule SR_5001_GX-2535410
 admin-state                                 enabled
 priority                                    150
 service-data-flow-id                        252001
 tcp-filter                                  all
 service-activation                          external-activation
 pcc-rule-name                               25510
 install-default-bearer-packet-filters-on-ue disabled
 packet-filter PF__25001_01
 !
 packet-filter PF__25001_02
 !
 packet-filter PF__25001_03
 !
 packet-filter PF__25001_04
 !
 packet-filter PF__25001_05
 !
 packet-filter PF__25001_06
 !
!

```

### example of task

1. create new SR same as `SR_5001_GX-2535410` but with `pcc-rule-name = 1111`
2. add this new SR and all other in RG `RG_klwkfelmflkewmfklwmming`
3. append this RG to billing-plan `BP-CORP-test`
4. save config for BP, RG, SR in file

#### 1.
```ipython
# if we want to use object after modification we need to copy it
In [11]: from copy import copy as cp

In [16]: newSR = cp(Sr['SR_5001_GX-2535410'])

In [17]: newSR.name = 'SR_5001_GX-2535410-new'

In [18]: newSR['pcc-rule-name'] = '1111'

In [19]: Sr[newSR.name] = newSR

In [20]: Sr.keys()
Out[20]: dict_keys(['SR_5001_GX-2535410', 'SR__5052', 'SR_wefwqfewf25001_GX-25X0', 'SR_5001_GX-2535410-new'])
```

#### 2.

```ipython
In [21]: for sr in Sr.keys():                                                                     
    ...:     Rg['RG_klwkfelmflkewmfklwmming']['service-rule'].append(sr)                          
    ...:                                                                                          
                                                                                                  
In [22]: an.show(Rg['RG_klwkfelmflkewmfklwmming'])                                                
services charging rating-group RG_klwkfelmflkewmfklwmming                                         
 charging-method            online                                                                
 quota-id                   10                                                                    
 priority                   29                                                                    
 admin-state                enabled                                                               
 multiplier                 1                                                                     
 measurement-method         volume                                                                
 volume-measurement-count   totalOctets                                                           
 volume-measurement-layer   layer3                                                                
 tcp-retransmission         charge                                                                
 quota-hold-time            9999999                                                               
 reporting-level            serviceRule                                                           
 volume-threshold           31489795728                                                           
 credit-authorization-event firstSdfPkt                                                           
 quota-black-list-timer     0                                                                     
 service-type               data                                                                  
 home-subscriber-charging   enabled                                                               
 roamer-subscriber-charging enabled                                                               
 enable-cdr                 true                                                                  
 ocs-response-grace-period  1                                                                     
 service-activation         always-on                                                             
 requested-unit-value       1572821312640                                                         
 service-rule SR_default_rs_roaming                                                               
 !                                                                                                
 service-rule SR_5001_GX-2535410                                                                  
 !                                                                                                
 service-rule SR__5052                                                                            
 !                                                                                                
 service-rule SR_wefwqfewf25001_GX-25X0                                                           
 !                                                                                                
 service-rule SR_5001_GX-2535410-new                                                              
 !                                                                                                
!                                                                                                 
```

#### 3.

```ipython
# create new sub-object for BP
In [22]: new_bp_rg = an.BP.RG('RG_klwkfelmflkewmfklwmming') 
  
# give him parameters                                                              
In [23]: new_bp_rg["fraud-charging"] = "false"                

# append this sub-object to BP                                                              
In [24]: Bp['BP-CORP-test']['rating-group'].append(new_bp_rg) 
                                                              
In [25]: an.show(Bp['BP-CORP-test'])                          
services charging billing-plan BP-CORP-test                   
 rating-group RG_10_CORP_test                                 
  fraud-charging false                                        
 !                                                                                                                    
 rating-group RG_klwkfelmflkewmfklwmming                      
  fraud-charging false                                        
 !                                                            
!                                                             
                                                              
```

#### 4.
```ipython
In [27]: filename = 'Test_ANparser\\newConf.txt'

In [28]: an.dump(Bp['BP-CORP-test'], filename)
Out[28]: <ANconf.Dump at 0x2833d2c7588>

# option file_append=True telling append printout to existen file
In [29]: an.dump(Rg['RG_klwkfelmflkewmfklwmming'], filename, file_append=True)
Out[29]: <ANconf.Dump at 0x2833d2854e0>

In [30]: for sr in Sr.values():
    ...:     an.dump(sr, filename, file_append=True)
    ...:

# now view file which is ready for load merge
!notepad Test_ANparser\newConf.txt

```