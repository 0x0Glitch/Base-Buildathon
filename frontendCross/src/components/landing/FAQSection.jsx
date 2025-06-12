// src/components/landing/FAQSection.jsx
import React from "react";
import { FrostedCard } from "../common/Cards";

const FAQSection = () => {
  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-slate-300">
            Everything you need to know about our cross-chain bridge
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <FrostedCard>
            <h3 className="text-xl font-bold mb-4">
              How does the cross-chain transfer work?
            </h3>
            <p className="text-slate-300">
              Our system uses a network of agents across supported chains that
              handle cross-chain minting and burning operations. When you
              deposit ETH, you receive sETH tokens which can be transferred
              across chains. The agents handle the burning on the source chain
              and minting on the destination chain.
            </p>
          </FrostedCard>

          <FrostedCard>
            <h3 className="text-xl font-bold mb-4">
              How do the cross-chain agents work?
            </h3>
            <p className="text-slate-300">
              Our agents are deployed across supported chains and execute the
              smart contract operations for cross-chain transfers. They handle
              the burning of sETH on the source chain and minting on the
              destination chain, ensuring secure and reliable transfers.
            </p>
          </FrostedCard>

          <FrostedCard>
            <h3 className="text-xl font-bold mb-4">
              Which chains are supported?
            </h3>
            <p className="text-slate-300">
              Currently, we support Ethereum, Optimism, Base, and Matic
              networks. We're constantly working to expand our chain support
              based on community demand and technical feasibility.
            </p>
          </FrostedCard>

          <FrostedCard>
            <h3 className="text-xl font-bold mb-4">
              Are there any transfer limits?
            </h3>
            <p className="text-slate-300">
              There are no minimum transfer amounts, but for security reasons,
              we implement maximum transfer limits that vary by chain. Please
              refer to our documentation for the most up-to-date information on
              transfer limits.
            </p>
          </FrostedCard>
        </div>
      </div>
    </section>
  );
};

export default FAQSection;
