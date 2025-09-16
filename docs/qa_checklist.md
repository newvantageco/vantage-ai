# Vantage AI - QA Checklist

This comprehensive checklist validates the entire user journey from onboarding to analytics. Use this to ensure all features work correctly before releases.

## Prerequisites

- [ ] Development environment is running (`make dev-up`)
- [ ] Demo data is seeded (`./scripts/seed_demo.sh`)
- [ ] All services are healthy (API, Web, Database)

## 1. Onboarding & Authentication

### 1.1 User Registration
- [ ] **Sign Up Flow**
  - [ ] Can create new account with email/password
  - [ ] Email verification works (check email)
  - [ ] User is redirected to organization setup after verification
  - [ ] Error handling for invalid emails/weak passwords

- [ ] **Organization Setup**
  - [ ] Can create new organization
  - [ ] Organization name is required and validated
  - [ ] User becomes admin of created organization
  - [ ] Redirected to dashboard after setup

### 1.2 User Login
- [ ] **Login Flow**
  - [ ] Can login with valid credentials
  - [ ] Invalid credentials show appropriate error
  - [ ] "Remember me" functionality works
  - [ ] Password reset flow works (if implemented)

- [ ] **Session Management**
  - [ ] Session persists across browser refreshes
  - [ ] Logout clears session properly
  - [ ] Session expires after appropriate time

## 2. Channel Connection

### 2.1 Meta/Facebook Integration
- [ ] **OAuth Flow**
  - [ ] Can initiate Meta OAuth connection
  - [ ] Redirects to Facebook login page
  - [ ] Can authorize app permissions
  - [ ] Returns to app with success/error handling
  - [ ] Channel appears in channels list

- [ ] **Channel Management**
  - [ ] Channel shows correct page name
  - [ ] Can disconnect channel
  - [ ] Reconnection works after disconnect
  - [ ] Error handling for expired tokens

### 2.2 LinkedIn Integration
- [ ] **OAuth Flow**
  - [ ] Can initiate LinkedIn OAuth connection
  - [ ] Redirects to LinkedIn authorization page
  - [ ] Can authorize app permissions
  - [ ] Returns to app with success/error handling
  - [ ] Channel appears in channels list

- [ ] **Channel Management**
  - [ ] Channel shows correct organization name
  - [ ] Can disconnect channel
  - [ ] Reconnection works after disconnect
  - [ ] Error handling for expired tokens

### 2.3 Channel Status
- [ ] **Connection Status**
  - [ ] Connected channels show "Active" status
  - [ ] Disconnected channels show "Inactive" status
  - [ ] Error states show appropriate messages
  - [ ] Last sync time is displayed correctly

## 3. Content Planning

### 3.1 Brand Guide
- [ ] **Brand Guide Creation**
  - [ ] Can create brand guide with voice, audience, pillars
  - [ ] All fields are optional but recommended
  - [ ] Brand guide saves correctly
  - [ ] Can edit existing brand guide

- [ ] **Brand Guide Usage**
  - [ ] Brand guide influences content suggestions
  - [ ] Voice guidelines are applied to generated content
  - [ ] Audience targeting works in content creation
  - [ ] Pillars are used for content categorization

### 3.2 Campaign Management
- [ ] **Campaign Creation**
  - [ ] Can create new campaign with name, objective, dates
  - [ ] Date validation works (end date after start date)
  - [ ] Campaign appears in campaigns list
  - [ ] Can edit campaign details

- [ ] **Campaign Organization**
  - [ ] Content items can be assigned to campaigns
  - [ ] Campaign view shows all associated content
  - [ ] Campaign performance metrics are tracked
  - [ ] Can archive/delete campaigns

### 3.3 Content Planning Engine
- [ ] **Content Suggestions**
  - [ ] Can generate content suggestions for date range
  - [ ] Suggestions align with brand pillars
  - [ ] Seasonal events are incorporated
  - [ ] Different content types are suggested

- [ ] **Planning Interface**
  - [ ] Calendar view shows suggested content
  - [ ] Can drag and drop content to different dates
  - [ ] Can accept/reject suggestions
  - [ ] Bulk operations work (accept all, reject all)

## 4. Content Creation

### 4.1 Content Item Creation
- [ ] **Basic Content**
  - [ ] Can create new content item
  - [ ] Title, caption, alt text fields work
  - [ ] First comment and hashtags can be added
  - [ ] Content saves as draft by default

- [ ] **Rich Content**
  - [ ] Can add images to content
  - [ ] Image upload works correctly
  - [ ] Alt text is required for accessibility
  - [ ] Image preview works in editor

- [ ] **Content Validation**
  - [ ] Safety checks work (inappropriate content detection)
  - [ ] Character limits are enforced
  - [ ] Required fields are validated
  - [ ] Error messages are clear and helpful

### 4.2 Content Editing
- [ ] **Edit Functionality**
  - [ ] Can edit existing content items
  - [ ] Changes save correctly
  - [ ] Version history is maintained (if implemented)
  - [ ] Can duplicate content items

- [ ] **Content Status**
  - [ ] Can change content status (draft → approved → scheduled)
  - [ ] Status changes are logged
  - [ ] Cannot edit posted content
  - [ ] Status workflow is enforced

## 5. Scheduling

### 5.1 Schedule Creation
- [ ] **Basic Scheduling**
  - [ ] Can schedule content to channels
  - [ ] Date/time picker works correctly
  - [ ] Can schedule to multiple channels
  - [ ] Timezone handling is correct

- [ ] **Schedule Management**
  - [ ] Scheduled content appears in calendar
  - [ ] Can edit scheduled times
  - [ ] Can cancel scheduled posts
  - [ ] Bulk scheduling works

### 5.2 Schedule Validation
- [ ] **Pre-schedule Checks**
  - [ ] Content is validated before scheduling
  - [ ] Channel connectivity is checked
  - [ ] Duplicate scheduling is prevented
  - [ ] Time conflicts are detected

- [ ] **Schedule Status**
  - [ ] Scheduled posts show correct status
  - [ ] Posted content shows success/failure status
  - [ ] Error messages are clear and actionable
  - [ ] Retry mechanism works for failed posts

## 6. Publishing

### 6.1 Post Publishing
- [ ] **Successful Publishing**
  - [ ] Content posts to connected channels
  - [ ] Post URLs are captured and stored
  - [ ] Publishing status updates correctly
  - [ ] Success notifications are shown

- [ ] **Error Handling**
  - [ ] Failed posts show error messages
  - [ ] Retry mechanism works
  - [ ] Partial failures are handled (some channels succeed, others fail)
  - [ ] Error logs are detailed and helpful

### 6.2 Post Management
- [ ] **Post Tracking**
  - [ ] Posted content is marked as "posted"
  - [ ] Post URLs are accessible
  - [ ] Can view post on original platform
  - [ ] Post metadata is stored correctly

## 7. Analytics & Metrics

### 7.1 Performance Tracking
- [ ] **Basic Metrics**
  - [ ] Views, likes, shares are tracked
  - [ ] Engagement rate is calculated correctly
  - [ ] Click-through rate is measured
  - [ ] Reach and impressions are recorded

- [ ] **Advanced Analytics**
  - [ ] Channel performance comparison
  - [ ] Content type performance analysis
  - [ ] Time-based performance trends
  - [ ] Audience engagement patterns

### 7.2 Reporting
- [ ] **Dashboard Metrics**
  - [ ] Key metrics are displayed prominently
  - [ ] Charts and graphs are accurate
  - [ ] Data refreshes correctly
  - [ ] Export functionality works

- [ ] **Weekly Briefs**
  - [ ] Can generate weekly performance briefs
  - [ ] Brief includes key insights and recommendations
  - [ ] Brief can be exported/shared
  - [ ] Brief content is relevant and actionable

## 8. User Experience

### 8.1 Navigation
- [ ] **Menu Navigation**
  - [ ] All main sections are accessible
  - [ ] Navigation is intuitive and consistent
  - [ ] Breadcrumbs work correctly
  - [ ] Search functionality works

- [ ] **Responsive Design**
  - [ ] App works on desktop (1920x1080, 1366x768)
  - [ ] App works on tablet (768x1024)
  - [ ] App works on mobile (375x667, 414x896)
  - [ ] Touch interactions work on mobile

### 8.2 Performance
- [ ] **Loading Times**
  - [ ] Pages load within 3 seconds
  - [ ] Images load progressively
  - [ ] API calls complete within 5 seconds
  - [ ] No memory leaks or performance degradation

- [ ] **Error Handling**
  - [ ] 404 pages are user-friendly
  - [ ] 500 errors show helpful messages
  - [ ] Network errors are handled gracefully
  - [ ] Loading states are shown during operations

## 9. Security & Data

### 9.1 Authentication Security
- [ ] **Session Security**
  - [ ] Sessions are properly secured
  - [ ] JWT tokens are validated correctly
  - [ ] Password requirements are enforced
  - [ ] Account lockout works after failed attempts

- [ ] **Data Protection**
  - [ ] Sensitive data is encrypted
  - [ ] API keys are stored securely
  - [ ] User data is not exposed in logs
  - [ ] GDPR compliance (if applicable)

### 9.2 API Security
- [ ] **Endpoint Security**
  - [ ] All endpoints require authentication
  - [ ] Rate limiting is implemented
  - [ ] CORS is configured correctly
  - [ ] Input validation prevents injection attacks

## 10. Integration Testing

### 10.1 End-to-End Flows
- [ ] **Complete User Journey**
  - [ ] User can complete full workflow: signup → connect channels → create content → schedule → publish → view analytics
  - [ ] No data loss during the process
  - [ ] All features work together seamlessly
  - [ ] Error recovery works at each step

### 10.2 Cross-Platform Testing
- [ ] **Multi-Channel Publishing**
  - [ ] Content publishes to all connected channels
  - [ ] Channel-specific formatting is applied
  - [ ] Platform-specific features work (hashtags, mentions, etc.)
  - [ ] Cross-platform analytics are accurate

## 11. Demo Data Validation

### 11.1 Demo Content
- [ ] **Content Quality**
  - [ ] Demo content is realistic and engaging
  - [ ] Images are appropriate and high-quality
  - [ ] Captions follow brand guidelines
  - [ ] Hashtags are relevant and trending

### 11.2 Demo Schedules
- [ ] **Schedule Timing**
  - [ ] Schedules are set for realistic times
  - [ ] Timezone handling is correct
  - [ ] Schedules don't conflict with each other
  - [ ] Schedule status updates correctly

## 12. Performance Benchmarks

### 12.1 Load Testing
- [ ] **Concurrent Users**
  - [ ] App handles 10+ concurrent users
  - [ ] Database performance is acceptable
  - [ ] API response times remain under 2 seconds
  - [ ] No memory leaks or crashes

### 12.2 Data Volume
- [ ] **Large Datasets**
  - [ ] App handles 1000+ content items
  - [ ] Analytics work with large datasets
  - [ ] Search and filtering remain fast
  - [ ] Pagination works correctly

## Sign-off

- [ ] **QA Lead Approval**: _________________ Date: _________
- [ ] **Product Manager Approval**: _________________ Date: _________
- [ ] **Engineering Lead Approval**: _________________ Date: _________

## Notes

_Use this space for any additional notes, known issues, or recommendations for future testing._

---

**Last Updated**: $(date)
**Version**: 1.0
**Next Review**: $(date -d '+1 month')
