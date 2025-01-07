# -----------------------------------------------------------
# Licensed Materials - Property of IBM
# 5737-M66, 5900-AAA
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.
# -----------------------------------------------------------

# This python script shows a simple model through which Sustainability offerings can interact in the SaaS pattern with a common ALM AppPoint pool. We'll
# see registration (provisioning), usage and deprovisioning. For clarity and simplicity, we do not perform validation of the certificate presented by the SLS service. Of course, you will want to 
# do this in your offering. 

import os, base64, time, urllib3, requests, json, sys , secrets , string , random
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

slsUrl = sys.argv[1]
slsRegistrationKey = sys.argv[2]

caCertificateForSSL = sys.argv[3]
print('slsUrl='+slsUrl)
print(slsRegistrationKey)
print("caCertificateForSSL")
print(caCertificateForSSL)
# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - Configuration section - you need to complete steps 1-5
# - 
# --------------------------------------------------------------------------------------------------------------------------------


def generate_api_key():
    alphabet = string.ascii_letters + string.digits
    temp= ''.join(secrets.choice(alphabet) for i in range(12))
    return "88"+ temp.lower()


# 1: Provide a name for your offering

offeringName = "aibroker"

# 2: Provide am identifier for your instance. This should be pseudounique, so chances of collisions are low. For example, based on the cluster 
#    identity, or a pseudo unique UUID created at initial installation time

instanceIdentifier = generate_api_key() #"xxxx"
#print("id")
print(instanceIdentifier)

# 3: Provide the SLS instance URL (SRE will give you this)

#slsUrl = "https://sls.ibm-sls.ibm-sls.apps.xxx.cp.fyre.ibm.com"

# 4: Provide the SLS registration key (SRE will give you this)

#slsRegistrationKey = "xxxx"

# 5: Decide if you want the demonstration to tear down your client afterwards (as you would do in a deprovision). If not, the client
#    will remain registered for you to experiment with.

# set it to be False Kewei
#deprovision=True
deprovision=False

# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - Demo section: preparation
# - 
# --------------------------------------------------------------------------------------------------------------------------------

# Prepare the SLS clientId to use, and prepare for storing client certificates that are generated at registration time.
slsClientId=offeringName+"-"+instanceIdentifier
certs_dir=f"{os.getcwd()}/certs"
clientCaCrtPath=certs_dir+"/"+slsClientId+"-ca.crt"
clientTlsCrtPath=certs_dir+"/"+slsClientId+"-tls.crt"
clientTlsKeyPath=certs_dir+"/"+slsClientId+"-tls.key"

#print ("Using clientId %s"%slsClientId)
#print ("Client certificates for interacting with SLS will be stored in "+certs_dir+"/"+slsClientId)

# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - Demo section: registration (provision) or reuse
# - 
# --------------------------------------------------------------------------------------------------------------------------------

# Let's check to see if client certificates already exist - if so, we can immediately move on to working with AppPoints. If not,
# we'll need to register ourselves with SLS to obtain the client certificates.

if os.path.isfile(clientCaCrtPath):
    # A client certificate appears to exist already. So let's use it.
    #print ("Discovered client certificates for SLS client "+slsClientId+". Let's use them.")
    pass
else:
    #print ("This appears to be a new SLS client. Let's attempt to register and obtain some client certificates.")
    pass

    # Make initial registration request
    print("will use certificate for client provisioning ")
    data = {'clientId': slsClientId, 'description': 'ALM sample client registration', 'role': 'manage'} # TODO: Rawa - Swagger docs incorrectly state 'id' rather than 'clientId'
    headers = {'X-Registration-Key': slsRegistrationKey} # TODO: Rawa - Swagger docs don't document the need for this critical header

    #print ("Making initial registration request for client "+slsClientId)
    response = requests.post(slsUrl+"/api/registrations",verify=False,json=data, headers=headers )     
    response.raise_for_status()

    registrationId = response.json()['registrationId']
    #print("Completing registration for registration request "+registrationId)

    #
    # Poll registration status until it's complete
    #
    provisioningWaiting = True
    while provisioningWaiting:
        headers = {'X-Registration-Key': slsRegistrationKey}
        response = requests.get(slsUrl+"/api/registrations/"+registrationId,verify=False,headers=headers )     
        response.raise_for_status()
        status = response.json()['state']
        print("Waiting for client provisioning to be completed. Current status: %s" %status)
        if status=="AWAITING_CONFIRMATION":
                # We are now ready to proceed; client certs are available
                #print ("Extracting client certificates")
                clientTlskey= base64.b64decode(response.json()['certs']['tls.key'])
                clientTlscrt= base64.b64decode(response.json()['certs']['tls.crt'])
                clientCacrt= base64.b64decode(response.json()['certs']['ca.crt'])
                with open(f'{clientTlsCrtPath}', 'wb') as f:
                    f.write(clientTlscrt)
                with open(f'{clientTlsKeyPath}', 'wb') as f:
                    f.write(clientTlskey)
                with open(f'{clientCaCrtPath}', 'wb') as f:
                    f.write(clientCacrt)
                provisioningWaiting = False        
        time.sleep(1)

    # The next step is to confirm the client. Poll status until complete.
    confirmationWaiting = True
    while confirmationWaiting:      
        response = requests.get(slsUrl+"/api/clients/"+slsClientId,verify=False, cert=(clientTlsCrtPath,clientTlsKeyPath))  
        #print (response)
        status = response.json()['state']
        #print("Waiting for client registration to be confirmed. Current status: %s" %status)
        if status=="REGISTERED":
            print ("Client registration confirmed.")
            confirmationWaiting = False        
        time.sleep(1)

# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - Demo section: Define helper functions to perform SLS actions: mirror AppPoint usage to SLS and obtain AppPoint usage from SLS
# - 
# --------------------------------------------------------------------------------------------------------------------------------

# Update 'quantity' AppPoints used in SLS. After 24 hours, the AppPoints will be automatically returned (ensuring no orphaned AppPoints if your service instance disappears) 
def spendAppPoints(quantity):
    #print ("Let's spend "+str(quantity)+" AppPoints")
    data = {'validity': 86400, 'quantity': quantity} 
    response = requests.put(slsUrl+"/api/products/"+productId+"/licensees/"+licenseeId,verify=False,json=data,headers = {'Content-type': 'application/json','X-Product-Version': "1.0" },cert=(clientTlsCrtPath,clientTlsKeyPath))     
    response.raise_for_status()

# String representation of AppPoint usage by your client. TODO: SLS will shortly be providing an update to correctly report usage for your client. At present, it returns the overall usage across all clients.
def getUsage():
    response = requests.get(slsUrl+"/api/tokens/",verify=False,params={"owner":slsClientId},cert=(clientTlsCrtPath,clientTlsKeyPath))     # This will require an SLS update to return usage specific to your owner
    response.raise_for_status()
    j = json.loads(response.content.decode('utf-8'))
    return j[0]['used']

# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - Demo section: Interact with AppPoints
# - 
# --------------------------------------------------------------------------------------------------------------------------------

# The ALM SaaS metering model is to perform the following actions every hour:
#   - Locally calculate your AppPoint usage (based on your individual pricing model)
#   - Check out the ValueMetric-Usage feature with (i) a licenseeId that is pseudo unique, (ii) an expiry of 86400 and (iii) a quantity matching the number of AppPoints
# 
# Note that at each hour, you simply update your AppPoint usage: you do not need to explicitly return your previous hour's AppPoints
#
# As an example, let's suppose your AppPoints are charged on (i) users and (ii) IOPoints. 
#   25 Users = 25 AppPoints
#   100 IOPoints = 10 AppPoints
# 
# You can use one of two approaches to check out AppPoints. 
# 
# SIMPLE "single shot"
# --------------------
#   - Report AppPoint usage in one go. 
#   - This means a single, consistent licenseeId at the instance level - for example, licenseeId="eis-126745fvabv", i.e. reusing the SLS clientId is convenient.
#   - Set the quantity to be 25+10 = 35
#
#
# COMPLEX "breakdown by capability"
# ---------------------------------
#   - Report AppPoint usage as a sequence of updates, per capability
#   - Enables you to use SLS as a way to understand unequivocally breakdown of AppPoint usage by capability
#   - Each capability has its own licenseeId - for example:
#           - example:  licenseeId="eis-126745fvabv-users",quantity=25
#                       licenseeId="eis-126745fvabv-iopoints",quantity=10
#  
# In this code example, we'll do a single shot for simplicity and clarity

# As described above, for simplicity in the single shot model, we set the licenseeId to the SLS clientId
licenseeId = slsClientId 

# Now let's define the license feature to check out. In SaaS ALM, this will be "MAS-ValueMetric-Usage"
productId = "MAS-ValueMetric-Usage" 

#
# Now let's start the day-to-day operation of the software - i.e., hourly updates of SLS of AppPoint usage, and hourly reporting of data (ready to send to DRO)
#

#print ("Simulating a few hours' usage. Note that you will require an ALM-ready version of SLS, and an ALM-ready license, to report AppPoint usage correctly in shared environments.")

# Hour 0: Check out 25+10=35 AppPoints
#print ("Hour 0")
#spendAppPoints(35)
# Get AppPoint usage from SLS (e.g., for reporting via DRO). 
#print("Usage: "+str(getUsage()))

# Hour 1: It's now 143 AppPoints overall
#print ("Hour 1")
#spendAppPoints(143)
#print("Usage: "+str(getUsage()))

# Hour 2: It's now 133 AppPoints overall
#print ("Hour 2")
#spendAppPoints(133)
#print("Usage: "+str(getUsage()))

# Hour 3: you get the picture :)
#
# ...

# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - Demo section: optional deprovision
# - 
# --------------------------------------------------------------------------------------------------------------------------------

# Now suppose a request has been made to deprovision your service. How do we gracefully decouple from SLS?
if deprovision:

# At deprovision, return your licenses and unregister the client
    print ("Preparing for deprovision: returning any AppPoints to the pool")
    response = requests.delete(slsUrl+"/api/products/"+productId+"/licensees/"+licenseeId,verify=False,cert=(clientTlsCrtPath,clientTlsKeyPath))     
    response.raise_for_status()
    print("Usage after deprovisioning: "+str(getUsage()))

    print ("Preparing for deprovision: unregistering the SLS client")
    response = requests.delete(slsUrl+"/api/clients/"+slsClientId,verify=False,cert=(clientTlsCrtPath,clientTlsKeyPath))     
    response.raise_for_status()
    #print ("Deleting redundant client certificates")
    os.remove(clientTlsCrtPath)
    os.remove(clientTlsKeyPath)
    os.remove(clientCaCrtPath)

else:
    #print ("No deprovisioning will occur. Your client is still registered with SLS.")
    pass

# --------------------------------------------------------------------------------------------------------------------------------
# - 
# - Demo section: end
# - 
# --------------------------------------------------------------------------------------------------------------------------------
#print ("Demo over.")
