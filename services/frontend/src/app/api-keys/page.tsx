"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Copy, Key, Plus, Trash2, Shield, AlertCircle } from 'lucide-react'
import { useAuth } from '@/lib/auth-context'
import { toast } from 'react-hot-toast'

interface ApiKey {
  id: string
  name: string
  key: string
  prefix: string
  createdAt: string
  lastUsed?: string
  permissions: string[]
}

export default function ApiKeysPage() {
  const { user, loading, isAuthenticated } = useAuth()
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [isCreating, setIsCreating] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyPermissions, setNewKeyPermissions] = useState<string[]>(['read'])
  const [showCreateForm, setShowCreateForm] = useState(false)

  useEffect(() => {
    if (isAuthenticated && user) {
      // Mock API keys for demo
      setApiKeys([
        {
          id: '1',
          name: 'Development Key',
          key: 'mk_dev_1234567890abcdef',
          prefix: 'mk_dev_',
          createdAt: '2024-01-15T10:30:00Z',
          lastUsed: '2024-01-20T14:45:00Z',
          permissions: ['read', 'write']
        },
        {
          id: '2',
          name: 'Production Key',
          key: 'mk_prod_0987654321fedcba',
          prefix: 'mk_prod_',
          createdAt: '2024-01-10T08:15:00Z',
          lastUsed: '2024-01-21T09:20:00Z',
          permissions: ['read']
        }
      ])
    }
  }, [isAuthenticated, user])

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) {
      toast.error('Please enter a key name')
      return
    }

    setIsCreating(true)

    // Simulate API call
    setTimeout(() => {
      const newKey: ApiKey = {
        id: Date.now().toString(),
        name: newKeyName,
        key: `mk_${Math.random().toString(36).substring(2, 15)}_${Math.random().toString(36).substring(2, 15)}`,
        prefix: 'mk_',
        createdAt: new Date().toISOString(),
        permissions: newKeyPermissions
      }

      setApiKeys(prev => [...prev, newKey])
      setNewKeyName('')
      setNewKeyPermissions(['read'])
      setShowCreateForm(false)
      setIsCreating(false)
      toast.success('API key created successfully!')
    }, 1000)
  }

  const handleDeleteKey = (keyId: string) => {
    setApiKeys(prev => prev.filter(key => key.id !== keyId))
    toast.success('API key deleted successfully!')
  }

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key)
    toast.success('API key copied to clipboard!')
  }

  const togglePermission = (permission: string) => {
    setNewKeyPermissions(prev =>
      prev.includes(permission)
        ? prev.filter(p => p !== permission)
        : [...prev, permission]
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Alert className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Please log in to access your API keys.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">API Keys</h1>
          <p className="text-muted-foreground mt-2">
            Manage your API keys for accessing Monkey Coder services
          </p>
        </div>
        <Button
          onClick={() => setShowCreateForm(true)}
          className="gap-2"
        >
          <Plus className="h-4 w-4" />
          Create New Key
        </Button>
      </div>

      {showCreateForm && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Create New API Key</CardTitle>
            <CardDescription>
              Generate a new API key for your applications
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="keyName">Key Name</Label>
              <Input
                id="keyName"
                placeholder="e.g., Production App, Development Testing"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>Permissions</Label>
              <div className="flex gap-2">
                {['read', 'write', 'delete'].map((permission) => (
                  <Badge
                    key={permission}
                    variant={newKeyPermissions.includes(permission) ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => togglePermission(permission)}
                  >
                    {permission}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleCreateKey}
                disabled={isCreating || !newKeyName.trim()}
              >
                {isCreating ? 'Creating...' : 'Create Key'}
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowCreateForm(false)}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="keys" className="w-full">
        <TabsList>
          <TabsTrigger value="keys">Your Keys</TabsTrigger>
          <TabsTrigger value="docs">Documentation</TabsTrigger>
        </TabsList>

        <TabsContent value="keys" className="space-y-4">
          {apiKeys.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Key className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No API keys yet</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Create your first API key to start using Monkey Coder services
                </p>
                <Button onClick={() => setShowCreateForm(true)}>
                  Create Your First Key
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {apiKeys.map((apiKey) => (
                <Card key={apiKey.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {apiKey.name}
                          <Badge variant="outline">
                            <Shield className="h-3 w-3 mr-1" />
                            {apiKey.permissions.join(', ')}
                          </Badge>
                        </CardTitle>
                        <CardDescription>
                          Created: {new Date(apiKey.createdAt).toLocaleDateString()}
                          {apiKey.lastUsed && (
                            <span className="ml-4">
                              Last used: {new Date(apiKey.lastUsed).toLocaleDateString()}
                            </span>
                          )}
                        </CardDescription>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteKey(apiKey.id)}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2">
                      <code className="bg-muted px-3 py-2 rounded text-sm font-mono">
                        {apiKey.key}
                      </code>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCopyKey(apiKey.key)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="docs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>API Documentation</CardTitle>
              <CardDescription>
                Learn how to use your API keys with Monkey Coder services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Authentication</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  Include your API key in the Authorization header of your requests:
                </p>
                <code className="block bg-muted p-3 rounded text-sm">
                  Authorization: Bearer YOUR_API_KEY
                </code>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Base URL</h4>
                <code className="block bg-muted p-3 rounded text-sm">
                  https://api.monkey-coder.com/v1
                </code>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Permissions</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• <strong>read</strong>: Access to code generation and model information</li>
                  <li>• <strong>write</strong>: Create and manage projects</li>
                  <li>• <strong>delete</strong>: Remove projects and data</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
