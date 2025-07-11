import React, { useState, useEffect } from 'react'
import { apiService } from '../services/api'

interface UserSettings {
  notifications: {
    email_notifications: boolean
    push_notifications: boolean
    trading_alerts: boolean
    price_alerts: boolean
    community_updates: boolean
  }
  trading: {
    auto_trading_enabled: boolean
    max_price_limit: number
    min_sale_price: number
    preferred_energy_source: string
    trading_hours_start: string
    trading_hours_end: string
  }
  security: {
    two_factor_enabled: boolean
    login_notifications: boolean
    api_access_enabled: boolean
  }
  privacy: {
    profile_visibility: string
    energy_data_sharing: boolean
    analytics_participation: boolean
  }
}

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'notifications' | 'trading' | 'security' | 'privacy'>('profile')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  // User profile data
  const [profile, setProfile] = useState({
    full_name: '',
    email: '',
    phone: '',
    location: '',
    bio: '',
    wallet_address: ''
  })

  // Settings data
  const [settings, setSettings] = useState<UserSettings>({
    notifications: {
      email_notifications: true,
      push_notifications: true,
      trading_alerts: true,
      price_alerts: true,
      community_updates: true
    },
    trading: {
      auto_trading_enabled: false,
      max_price_limit: 0.20,
      min_sale_price: 0.10,
      preferred_energy_source: 'renewable',
      trading_hours_start: '09:00',
      trading_hours_end: '18:00'
    },
    security: {
      two_factor_enabled: false,
      login_notifications: true,
      api_access_enabled: false
    },
    privacy: {
      profile_visibility: 'community',
      energy_data_sharing: true,
      analytics_participation: true
    }
  })

  // Password change
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  })

  useEffect(() => {
    loadUserData()
  }, [])

  const loadUserData = async () => {
    setLoading(true)
    try {
      const user = await apiService.getCurrentUser()
      setProfile({
        full_name: user.full_name,
        email: user.email,
        phone: user.phone || '',
        location: user.location || '',
        bio: user.bio || '',
        wallet_address: user.wallet_address || ''
      })
      
      // Load user settings (this would come from a settings endpoint)
      // const userSettings = await apiService.getUserSettings()
      // setSettings(userSettings)
    } catch (error) {
      console.error('Failed to load user data:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      await apiService.updateUser(profile)
      alert('Profile updated successfully!')
    } catch (error) {
      console.error('Failed to update profile:', error)
      alert('Failed to update profile. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const saveSettings = async () => {
    setSaving(true)
    try {
      // This would call apiService.updateUserSettings(settings)
      await new Promise(resolve => setTimeout(resolve, 1000)) // Mock delay
      alert('Settings saved successfully!')
    } catch (error) {
      console.error('Failed to save settings:', error)
      alert('Failed to save settings. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      alert('New passwords do not match!')
      return
    }

    setSaving(true)
    try {
      await apiService.changePassword(passwordForm.current_password, passwordForm.new_password)
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: ''
      })
      alert('Password changed successfully!')
    } catch (error) {
      console.error('Failed to change password:', error)
      alert('Failed to change password. Please check your current password.')
    } finally {
      setSaving(false)
    }
  }

  const enableTwoFactor = async () => {
    try {
      const qrCode = await apiService.enableTwoFactor()
      // Show QR code modal for user to scan
      alert('Two-factor authentication setup initiated. Please scan the QR code with your authenticator app.')
    } catch (error) {
      console.error('Failed to enable 2FA:', error)
      alert('Failed to enable two-factor authentication.')
    }
  }

  const disableTwoFactor = async () => {
    try {
      await apiService.disableTwoFactor()
      setSettings({
        ...settings,
        security: {
          ...settings.security,
          two_factor_enabled: false
        }
      })
      alert('Two-factor authentication disabled.')
    } catch (error) {
      console.error('Failed to disable 2FA:', error)
      alert('Failed to disable two-factor authentication.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-2">Manage your account preferences and security settings</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <nav className="space-y-1">
              {[
                { key: 'profile', label: 'Profile', icon: '👤' },
                { key: 'notifications', label: 'Notifications', icon: '🔔' },
                { key: 'trading', label: 'Trading', icon: '⚡' },
                { key: 'security', label: 'Security', icon: '🔒' },
                { key: 'privacy', label: 'Privacy', icon: '👁️' }
              ].map((item) => (
                <button
                  key={item.key}
                  onClick={() => setActiveTab(item.key as any)}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    activeTab === item.key
                      ? 'bg-green-100 text-green-700 border-r-2 border-green-500'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <span className="mr-3">{item.icon}</span>
                  {item.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
                <p className="text-gray-600 mt-4">Loading settings...</p>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow">
                {/* Profile Settings */}
                {activeTab === 'profile' && (
                  <div className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-6">Profile Information</h3>
                    <form onSubmit={saveProfile} className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Full Name</label>
                          <input
                            type="text"
                            value={profile.full_name}
                            onChange={(e) => setProfile({...profile, full_name: e.target.value})}
                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Email</label>
                          <input
                            type="email"
                            value={profile.email}
                            onChange={(e) => setProfile({...profile, email: e.target.value})}
                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Phone</label>
                          <input
                            type="tel"
                            value={profile.phone}
                            onChange={(e) => setProfile({...profile, phone: e.target.value})}
                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Location</label>
                          <input
                            type="text"
                            value={profile.location}
                            onChange={(e) => setProfile({...profile, location: e.target.value})}
                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Bio</label>
                        <textarea
                          rows={3}
                          value={profile.bio}
                          onChange={(e) => setProfile({...profile, bio: e.target.value})}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          placeholder="Tell us about yourself..."
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Wallet Address</label>
                        <input
                          type="text"
                          value={profile.wallet_address}
                          onChange={(e) => setProfile({...profile, wallet_address: e.target.value})}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          placeholder="0x..."
                        />
                        <p className="text-sm text-gray-500 mt-1">Your blockchain wallet address for energy transactions</p>
                      </div>
                      <div className="flex justify-end">
                        <button
                          type="submit"
                          disabled={saving}
                          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition duration-200 disabled:opacity-50"
                        >
                          {saving ? 'Saving...' : 'Save Profile'}
                        </button>
                      </div>
                    </form>

                    {/* Password Change Section */}
                    <div className="mt-8 pt-8 border-t border-gray-200">
                      <h4 className="text-md font-medium text-gray-900 mb-4">Change Password</h4>
                      <form onSubmit={changePassword} className="space-y-4 max-w-md">
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Current Password</label>
                          <input
                            type="password"
                            value={passwordForm.current_password}
                            onChange={(e) => setPasswordForm({...passwordForm, current_password: e.target.value})}
                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">New Password</label>
                          <input
                            type="password"
                            value={passwordForm.new_password}
                            onChange={(e) => setPasswordForm({...passwordForm, new_password: e.target.value})}
                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Confirm New Password</label>
                          <input
                            type="password"
                            value={passwordForm.confirm_password}
                            onChange={(e) => setPasswordForm({...passwordForm, confirm_password: e.target.value})}
                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          />
                        </div>
                        <button
                          type="submit"
                          disabled={saving}
                          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200 disabled:opacity-50"
                        >
                          {saving ? 'Changing...' : 'Change Password'}
                        </button>
                      </form>
                    </div>
                  </div>
                )}

                {/* Notification Settings */}
                {activeTab === 'notifications' && (
                  <div className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-6">Notification Preferences</h3>
                    <div className="space-y-6">
                      {[
                        { key: 'email_notifications', label: 'Email Notifications', description: 'Receive notifications via email' },
                        { key: 'push_notifications', label: 'Push Notifications', description: 'Receive push notifications in browser' },
                        { key: 'trading_alerts', label: 'Trading Alerts', description: 'Get notified about trading opportunities' },
                        { key: 'price_alerts', label: 'Price Alerts', description: 'Get notified about significant price changes' },
                        { key: 'community_updates', label: 'Community Updates', description: 'Receive updates from your communities' }
                      ].map((item) => (
                        <div key={item.key} className="flex items-center justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">{item.label}</h4>
                            <p className="text-sm text-gray-500">{item.description}</p>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={settings.notifications[item.key as keyof typeof settings.notifications]}
                              onChange={(e) => setSettings({
                                ...settings,
                                notifications: {
                                  ...settings.notifications,
                                  [item.key]: e.target.checked
                                }
                              })}
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                          </label>
                        </div>
                      ))}
                    </div>
                    <div className="mt-6">
                      <button
                        onClick={saveSettings}
                        disabled={saving}
                        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition duration-200 disabled:opacity-50"
                      >
                        {saving ? 'Saving...' : 'Save Notification Settings'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Trading Settings */}
                {activeTab === 'trading' && (
                  <div className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-6">Trading Preferences</h3>
                    <div className="space-y-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">Auto Trading</h4>
                          <p className="text-sm text-gray-500">Enable automatic trading based on your preferences</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={settings.trading.auto_trading_enabled}
                            onChange={(e) => setSettings({
                              ...settings,
                              trading: {
                                ...settings.trading,
                                auto_trading_enabled: e.target.checked
                              }
                            })}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                        </label>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Max Price Limit ($/kWh)</label>
                          <input
                            type="number"
                            step="0.01"
                            value={settings.trading.max_price_limit}
                            onChange={(e) => setSettings({
                              ...settings,
                              trading: {
                                ...settings.trading,
                                max_price_limit: parseFloat(e.target.value)
                              }
                            })}
                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Min Sale Price ($/kWh)</label>
                          <input
                            type="number"
                            step="0.01"
                            value={settings.trading.min_sale_price}
                            onChange={(e) => setSettings({
                              ...settings,
                              trading: {
                                ...settings.trading,
                                min_sale_price: parseFloat(e.target.value)
                              }
                            })}
                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Preferred Energy Source</label>
                          <select
                            value={settings.trading.preferred_energy_source}
                            onChange={(e) => setSettings({
                              ...settings,
                              trading: {
                                ...settings.trading,
                                preferred_energy_source: e.target.value
                              }
                            })}
                            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                          >
                            <option value="any">Any Source</option>
                            <option value="renewable">Renewable Only</option>
                            <option value="solar">Solar Only</option>
                            <option value="wind">Wind Only</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Trading Hours</label>
                          <div className="grid grid-cols-2 gap-2">
                            <input
                              type="time"
                              value={settings.trading.trading_hours_start}
                              onChange={(e) => setSettings({
                                ...settings,
                                trading: {
                                  ...settings.trading,
                                  trading_hours_start: e.target.value
                                }
                              })}
                              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                            />
                            <input
                              type="time"
                              value={settings.trading.trading_hours_end}
                              onChange={(e) => setSettings({
                                ...settings,
                                trading: {
                                  ...settings.trading,
                                  trading_hours_end: e.target.value
                                }
                              })}
                              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="mt-6">
                      <button
                        onClick={saveSettings}
                        disabled={saving}
                        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition duration-200 disabled:opacity-50"
                      >
                        {saving ? 'Saving...' : 'Save Trading Settings'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Security Settings */}
                {activeTab === 'security' && (
                  <div className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-6">Security Settings</h3>
                    <div className="space-y-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">Two-Factor Authentication</h4>
                          <p className="text-sm text-gray-500">Add an extra layer of security to your account</p>
                        </div>
                        <div>
                          {settings.security.two_factor_enabled ? (
                            <button
                              onClick={disableTwoFactor}
                              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition duration-200"
                            >
                              Disable 2FA
                            </button>
                          ) : (
                            <button
                              onClick={enableTwoFactor}
                              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition duration-200"
                            >
                              Enable 2FA
                            </button>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">Login Notifications</h4>
                          <p className="text-sm text-gray-500">Get notified of new logins to your account</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={settings.security.login_notifications}
                            onChange={(e) => setSettings({
                              ...settings,
                              security: {
                                ...settings.security,
                                login_notifications: e.target.checked
                              }
                            })}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                        </label>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">API Access</h4>
                          <p className="text-sm text-gray-500">Enable API access for third-party integrations</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={settings.security.api_access_enabled}
                            onChange={(e) => setSettings({
                              ...settings,
                              security: {
                                ...settings.security,
                                api_access_enabled: e.target.checked
                              }
                            })}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                        </label>
                      </div>
                    </div>
                    <div className="mt-6">
                      <button
                        onClick={saveSettings}
                        disabled={saving}
                        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition duration-200 disabled:opacity-50"
                      >
                        {saving ? 'Saving...' : 'Save Security Settings'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Privacy Settings */}
                {activeTab === 'privacy' && (
                  <div className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-6">Privacy Settings</h3>
                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Profile Visibility</label>
                        <select
                          value={settings.privacy.profile_visibility}
                          onChange={(e) => setSettings({
                            ...settings,
                            privacy: {
                              ...settings.privacy,
                              profile_visibility: e.target.value
                            }
                          })}
                          className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
                        >
                          <option value="public">Public - Visible to everyone</option>
                          <option value="community">Community - Visible to community members only</option>
                          <option value="private">Private - Not visible to others</option>
                        </select>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">Energy Data Sharing</h4>
                          <p className="text-sm text-gray-500">Share your energy usage data for research purposes</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={settings.privacy.energy_data_sharing}
                            onChange={(e) => setSettings({
                              ...settings,
                              privacy: {
                                ...settings.privacy,
                                energy_data_sharing: e.target.checked
                              }
                            })}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                        </label>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">Analytics Participation</h4>
                          <p className="text-sm text-gray-500">Help improve the platform by sharing usage analytics</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={settings.privacy.analytics_participation}
                            onChange={(e) => setSettings({
                              ...settings,
                              privacy: {
                                ...settings.privacy,
                                analytics_participation: e.target.checked
                              }
                            })}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                        </label>
                      </div>
                    </div>
                    <div className="mt-6">
                      <button
                        onClick={saveSettings}
                        disabled={saving}
                        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition duration-200 disabled:opacity-50"
                      >
                        {saving ? 'Saving...' : 'Save Privacy Settings'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
