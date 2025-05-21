param location string = resourceGroup().location

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: 'myKeyVaultBost2025' // zmień na unikalną nazwę!
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      name: 'standard'
      family: 'A'
    }
    accessPolicies: []
    enableSoftDelete: true
    enablePurgeProtection: true
  }
}
