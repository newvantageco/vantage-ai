"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { PLANS, getPlanById, formatPrice, getYearlyDiscount } from "@/lib/plans";

interface BillingInfo {
  org_id: string;
  plan: string;
  status: string;
  current_period_end?: string;
  days_until_renewal?: number;
  stripe_customer_id?: string;
}

interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
}

interface PortalResponse {
  portal_url: string;
}

export default function BillingPage() {
  const [billingInfo, setBillingInfo] = useState<BillingInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null);
  const [portalLoading, setPortalLoading] = useState(false);

  useEffect(() => {
    const fetchBillingInfo = async () => {
      try {
        setLoading(true);
        const response = await api.get<BillingInfo>("/billing/info");
        setBillingInfo(response.data);
      } catch (error) {
        console.error("Failed to fetch billing info:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchBillingInfo();
  }, []);

  const handleUpgrade = async (planId: string) => {
    try {
      setCheckoutLoading(planId);
      const response = await api.post<CheckoutResponse>("/billing/checkout", {
        plan: planId,
        success_url: `${window.location.origin}/billing?success=true`,
        cancel_url: `${window.location.origin}/billing?canceled=true`,
      });
      
      // Redirect to Stripe checkout
      window.location.href = response.data.checkout_url;
    } catch (error) {
      console.error("Failed to create checkout session:", error);
      alert("Failed to start checkout process. Please try again.");
    } finally {
      setCheckoutLoading(null);
    }
  };

  const handleManageBilling = async () => {
    try {
      setPortalLoading(true);
      const response = await api.get<PortalResponse>("/billing/portal", {
        params: {
          return_url: `${window.location.origin}/billing`,
        },
      });
      
      // Redirect to Stripe customer portal
      window.location.href = response.data.portal_url;
    } catch (error) {
      console.error("Failed to create portal session:", error);
      alert("Failed to open billing portal. Please try again.");
    } finally {
      setPortalLoading(false);
    }
  };

  const currentPlan = billingInfo ? getPlanById(billingInfo.plan) : null;

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Billing & Plans</h1>
            <p className="text-gray-600 mt-2">
              Manage your subscription and billing information
            </p>
          </div>
          <Link
            href="/privacy"
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Privacy Settings
          </Link>
        </div>
      </div>

      {/* Current Plan Status */}
      {billingInfo && currentPlan && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Current Plan: {currentPlan.name}
              </h2>
              <p className="text-gray-600 mt-1">
                {currentPlan.description}
              </p>
              {billingInfo.days_until_renewal && (
                <p className="text-sm text-gray-500 mt-2">
                  Renews in {billingInfo.days_until_renewal} days
                </p>
              )}
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">
                {formatPrice(currentPlan.price.monthly)}/month
              </div>
              <button
                onClick={handleManageBilling}
                disabled={portalLoading}
                className="mt-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 disabled:opacity-50"
              >
                {portalLoading ? "Opening..." : "Manage Billing"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Available Plans */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.values(PLANS).map((plan) => {
            const isCurrentPlan = billingInfo?.plan === plan.id;
            const isPopular = plan.popular;
            const yearlyDiscount = getYearlyDiscount(plan.price.monthly, plan.price.yearly);

            return (
              <div
                key={plan.id}
                className={`relative bg-white rounded-lg shadow-sm border p-6 ${
                  isPopular ? "ring-2 ring-blue-500" : ""
                } ${isCurrentPlan ? "bg-blue-50" : ""}`}
              >
                {isPopular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                {isCurrentPlan && (
                  <div className="absolute -top-3 right-4">
                    <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                      Current Plan
                    </span>
                  </div>
                )}

                <div className="text-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-900">{plan.name}</h3>
                  <p className="text-gray-600 mt-2">{plan.description}</p>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-gray-900">
                      {formatPrice(plan.price.monthly)}
                    </span>
                    <span className="text-gray-600">/month</span>
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    or {formatPrice(plan.price.yearly)}/year ({yearlyDiscount}% off)
                  </div>
                </div>

                <div className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <div key={index} className="flex items-center">
                      <div className={`w-4 h-4 rounded-full mr-3 ${
                        feature.included ? "bg-green-500" : "bg-gray-300"
                      }`}>
                        {feature.included && (
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <span className={`text-sm ${
                        feature.included ? "text-gray-900" : "text-gray-400"
                      }`}>
                        {feature.name}
                        {feature.limit && (
                          <span className="text-gray-500 ml-1">({feature.limit})</span>
                        )}
                      </span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={isCurrentPlan || checkoutLoading === plan.id}
                  className={`w-full py-2 px-4 rounded-md font-medium ${
                    isCurrentPlan
                      ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                      : isPopular
                      ? "bg-blue-600 text-white hover:bg-blue-700"
                      : "bg-gray-900 text-white hover:bg-gray-800"
                  } disabled:opacity-50`}
                >
                  {isCurrentPlan
                    ? "Current Plan"
                    : checkoutLoading === plan.id
                    ? "Processing..."
                    : `Upgrade to ${plan.name}`
                  }
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Agency Consolidated Billing Placeholder */}
      <div className="bg-blue-50 rounded-lg border border-blue-200 p-6 mb-8">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-8 w-8 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-lg font-medium text-blue-800">Agency Billing</h3>
            <p className="text-blue-700 mt-1">
              Consolidated billing for multiple client organizations coming soon. 
              Manage all your client accounts from a single invoice.
            </p>
          </div>
        </div>
      </div>

      {/* Usage Information */}
      {billingInfo && currentPlan && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Plan Limits</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Posts per Month</div>
              <div className="text-2xl font-bold text-gray-900">
                {currentPlan.limits.postsPerMonth}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Social Channels</div>
              <div className="text-2xl font-bold text-gray-900">
                {currentPlan.limits.channels}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Team Members</div>
              <div className="text-2xl font-bold text-gray-900">
                {currentPlan.limits.users}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Campaigns</div>
              <div className="text-2xl font-bold text-gray-900">
                {currentPlan.limits.campaigns}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Content Items</div>
              <div className="text-2xl font-bold text-gray-900">
                {currentPlan.limits.contentItems}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">AI Generations</div>
              <div className="text-2xl font-bold text-gray-900">
                {currentPlan.limits.aiGenerations}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
