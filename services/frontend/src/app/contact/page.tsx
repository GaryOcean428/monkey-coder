"use client"

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FormField } from '@/components/ui/form-field'
import { FormStatus, useFormStatus } from '@/components/ui/form-status'
import { Mail, MessageSquare, Phone } from 'lucide-react'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { validateEmail, validateName, validateSubject } from '@/lib/validation'
import * as z from 'zod'

const contactSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  subject: z.string().min(5, 'Subject must be at least 5 characters'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
})

type ContactFormData = z.infer<typeof contactSchema>

export default function ContactPage() {
  const formStatus = useFormStatus()

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    reset,
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
  })

  const watchedName = watch('name')
  const watchedEmail = watch('email')
  const watchedSubject = watch('subject')
  const watchedMessage = watch('message')

  const onSubmit = async (_data: ContactFormData) => {
    formStatus.setSubmitting('Sending your message...')

    try {
      // Simulate form submission with realistic delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      formStatus.setSuccess(
        'Message sent successfully!',
        'Thank you for contacting us. We\'ll get back to you within 24 hours.'
      )
      
      // Reset form after success
      reset()
    } catch (error) {
      console.error('Contact form error:', error)
      formStatus.setError(
        'Failed to send message',
        'There was an error sending your message. Please try again.'
      )
    }
  }

  return (
    <div className="container mx-auto py-16 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Contact Us</h1>
          <p className="text-lg text-muted-foreground">
            Have questions about Monkey Coder? We're here to help!
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <Card>
            <CardHeader>
              <Mail className="h-8 w-8 mb-2 text-primary" />
              <CardTitle>Email</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">support@monkey-coder.com</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <MessageSquare className="h-8 w-8 mb-2 text-primary" />
              <CardTitle>Live Chat</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Available Mon-Fri, 9am-5pm PST</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Phone className="h-8 w-8 mb-2 text-primary" />
              <CardTitle>Enterprise</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Schedule a demo call</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Send us a message</CardTitle>
            <CardDescription>
              Fill out the form below and we'll get back to you within 24 hours
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Form Status */}
            <FormStatus 
              status={formStatus.status}
              message={formStatus.message}
              details={formStatus.details}
              className="mb-6"
              autoHideSuccess={8000}
              onStatusChange={formStatus.updateStatus}
            />

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-4">
                <FormField
                  id="name"
                  label="Name"
                  placeholder="Your name"
                  {...register('name')}
                  error={errors.name?.message}
                  success={!!(watchedName && !errors.name && watchedName.length >= 2)}
                  helperText="Your full name"
                  onValidation={(value) => validateName(value, "Name")}
                  required
                />
                
                <FormField
                  id="email"
                  label="Email"
                  type="email"
                  placeholder="your@email.com"
                  {...register('email')}
                  error={errors.email?.message}
                  success={!!(watchedEmail && !errors.email && watchedEmail.includes('@'))}
                  helperText="We'll use this to respond to you"
                  onValidation={validateEmail}
                  required
                />
              </div>

              <FormField
                id="subject"
                label="Subject"
                placeholder="How can we help?"
                {...register('subject')}
                error={errors.subject?.message}
                success={!!(watchedSubject && !errors.subject && watchedSubject.length >= 5)}
                helperText="Brief description of your inquiry"
                onValidation={validateSubject}
                required
              />

              <div className="space-y-2">
                <label htmlFor="message" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  Message *
                </label>
                <textarea
                  id="message"
                  {...register('message')}
                  rows={6}
                  className="w-full px-3 py-2 text-sm rounded-md border border-input bg-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="Tell us more about your inquiry..."
                />
                {errors.message && (
                  <p className="text-sm text-destructive">{errors.message.message}</p>
                )}
                {watchedMessage && (
                  <p className="text-xs text-muted-foreground">
                    {watchedMessage.length}/2000 characters
                  </p>
                )}
              </div>

              <div className="flex gap-4">
                <Button 
                  type="submit" 
                  disabled={formStatus.status === 'submitting'}
                  className="min-w-[120px]"
                >
                  {formStatus.status === 'submitting' ? 'Sending...' : 'Send Message'}
                </Button>
                <Link href="/">
                  <Button variant="outline">Cancel</Button>
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
