'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar as CalendarIcon, Plus, Edit, Trash2, Clock } from "lucide-react"
import { format, isToday, isSameDay } from 'date-fns'

interface Schedule {
  id: string
  content_item_id: string
  channel_id: string
  scheduled_at: string
  status: string
  caption?: string
  channel_name?: string
  title?: string
}

interface ModernCalendarProps {
  schedules: Schedule[]
  onDateSelect: (date: Date) => void
  onScheduleCreate: (data: any) => void
  onScheduleEdit: (schedule: Schedule) => void
  onScheduleDelete: (scheduleId: string) => void
}

export function ModernCalendar({ 
  schedules, 
  onDateSelect, 
  onScheduleCreate, 
  onScheduleEdit, 
  onScheduleDelete 
}: ModernCalendarProps) {
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date())
  const [showCreateForm, setShowCreateForm] = useState(false)

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'posted': return 'default'
      case 'scheduled': return 'secondary'
      case 'draft': return 'outline'
      case 'failed': return 'destructive'
      default: return 'outline'
    }
  }

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'linkedin': return 'bg-blue-100 text-blue-800'
      case 'facebook': return 'bg-blue-100 text-blue-800'
      case 'instagram': return 'bg-pink-100 text-pink-800'
      case 'twitter': return 'bg-sky-100 text-sky-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getChannelName = (schedule: Schedule) => {
    return schedule.channel_name || schedule.channel_id || 'Unknown'
  }

  const getSchedulesForDate = (date: Date) => {
    return schedules.filter(schedule => 
      isSameDay(new Date(schedule.scheduled_at), date)
    )
  }

  const handleDateSelect = (date: Date | undefined) => {
    setSelectedDate(date)
    if (date) {
      onDateSelect(date)
    }
  }

  const handleCreateSchedule = (formData: any) => {
    onScheduleCreate(formData)
    setShowCreateForm(false)
  }

  return (
    <div className="space-y-6">
      {/* Calendar Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CalendarIcon className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Content Calendar</h2>
        </div>
        <Button 
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Plus className="h-4 w-4 mr-2" />
          Schedule Content
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Calendar View</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-1 text-center">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="p-2 font-semibold text-gray-600">{day}</div>
                ))}
                {Array.from({ length: 35 }, (_, i) => {
                  const date = new Date()
                  date.setDate(i - 6)
                  const isCurrentMonth = date.getMonth() === new Date().getMonth()
                  const isSelected = selectedDate && isSameDay(date, selectedDate)
                  const isToday = isSameDay(date, new Date())
                  
                  return (
                    <button
                      key={i}
                      onClick={() => handleDateSelect(date)}
                      className={`h-12 w-12 rounded-md text-sm hover:bg-gray-100 ${
                        isSelected ? 'bg-blue-600 text-white' : 
                        isToday ? 'bg-blue-50 text-blue-600 font-semibold' :
                        isCurrentMonth ? 'text-gray-900' : 'text-gray-400'
                      }`}
                    >
                      {date.getDate()}
                    </button>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Selected Date Schedules */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">
                {selectedDate ? format(selectedDate, 'MMMM d, yyyy') : 'Select a date'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedDate ? (
                <div className="space-y-3">
                  {getSchedulesForDate(selectedDate).length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <CalendarIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                      <p>No schedules for this date</p>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="mt-3"
                        onClick={() => setShowCreateForm(true)}
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        Add Schedule
                      </Button>
                    </div>
                  ) : (
                    getSchedulesForDate(selectedDate).map((schedule) => (
                      <div key={schedule.id} className="border rounded-lg p-3 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2 flex-1">
                            <h4 className="font-semibold text-sm text-gray-900">
                              {schedule.title || 'Untitled'}
                            </h4>
                            <p className="text-xs text-gray-600 line-clamp-2">
                              {schedule.caption || 'No description'}
                            </p>
                            <div className="flex items-center gap-2">
                              <span className={`px-2 py-1 rounded-full text-xs ${
                                schedule.status === 'posted' ? 'bg-green-100 text-green-800' :
                                schedule.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                                schedule.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {schedule.status}
                              </span>
                              <span className={`px-2 py-1 rounded-full text-xs ${getChannelColor(getChannelName(schedule))}`}>
                                {getChannelName(schedule)}
                              </span>
                            </div>
                            <div className="flex items-center gap-1 text-xs text-gray-500">
                              <Clock className="h-3 w-3" />
                              {format(new Date(schedule.scheduled_at), 'h:mm a')}
                            </div>
                          </div>
                          <div className="flex gap-1 ml-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => onScheduleEdit(schedule)}
                              className="h-8 w-8 p-0"
                            >
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => onScheduleDelete(schedule.id)}
                              className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CalendarIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                  <p>Select a date to view schedules</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Create Schedule Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Create New Schedule</h3>
            <ScheduleForm
              onSubmit={handleCreateSchedule}
              onCancel={() => setShowCreateForm(false)}
              selectedDate={selectedDate}
            />
          </div>
        </div>
      )}
    </div>
  )
}

// Schedule Form Component
interface ScheduleFormProps {
  onSubmit: (data: any) => void
  onCancel: () => void
  selectedDate?: Date
}

function ScheduleForm({ onSubmit, onCancel, selectedDate }: ScheduleFormProps) {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    channel: '',
    scheduledAt: selectedDate ? format(selectedDate, "yyyy-MM-dd'T'HH:mm") : '',
    status: 'draft'
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Title
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter content title"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Channel
        </label>
        <select
          value={formData.channel}
          onChange={(e) => setFormData({...formData, channel: e.target.value})}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        >
          <option value="">Select channel</option>
          <option value="linkedin">LinkedIn</option>
          <option value="facebook">Facebook</option>
          <option value="instagram">Instagram</option>
          <option value="twitter">Twitter</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Content
        </label>
        <textarea
          value={formData.content}
          onChange={(e) => setFormData({...formData, content: e.target.value})}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Write your content here..."
          rows={3}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Schedule Date & Time
        </label>
        <input
          type="datetime-local"
          value={formData.scheduledAt}
          onChange={(e) => setFormData({...formData, scheduledAt: e.target.value})}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white">
          Create Schedule
        </Button>
      </div>
    </form>
  )
}
