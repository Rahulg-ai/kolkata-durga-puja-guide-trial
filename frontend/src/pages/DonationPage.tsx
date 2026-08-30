import {
  useEffect,
  useMemo,
  useState,
} from "react";

import API_BASE_URL from "../api";

import "./DonationPage.css";


declare global {
  interface Window {
    Razorpay: any;
  }
}


type DonationPageProps = {
  onBack: () => void;
};


/* =====================================================
   SUPPORTER TIERS
   ===================================================== */

const SUPPORTER_TIERS = [
  {
    amount: 1000,
    title: "Maa's Main Character",
    icon: "👑",
  },
  {
    amount: 500,
    title: "Maha Bhakt",
    icon: "🪷",
  },
  {
    amount: 250,
    title: "Maa's Inner Circle",
    icon: "🌼",
  },
  {
    amount: 200,
    title: "Pujo Pro",
    icon: "✨",
  },
  {
    amount: 150,
    title: "Dhak Crew",
    icon: "🕺",
  },
  {
    amount: 100,
    title: "Pujo Squad",
    icon: "🎉",
  },
  {
    amount: 50,
    title: "Dhak Dost",
    icon: "🪔",
  },
  {
    amount: 1,
    title: "Pujo Bestie",
    icon: "🌺",
  },
];


const PRESET_AMOUNTS = [
  50,
  100,
  150,
  200,
  250,
  500,
  1000,
];


const MIN_DONATION = 1;
const MAX_DONATION = 100000;


/* =====================================================
   SUPPORTER TIER HELPERS
   ===================================================== */

function getSupporterTier(
  amount: number
) {
  return (
    SUPPORTER_TIERS.find(
      (tier) =>
        amount >= tier.amount
    ) ??
    SUPPORTER_TIERS[
      SUPPORTER_TIERS.length - 1
    ]
  );
}


function getNextSupporterTier(
  amount: number
) {
  return [...SUPPORTER_TIERS]
    .reverse()
    .find(
      (tier) =>
        amount < tier.amount
    );
}


function getSupporterMessage(
  amount: number
) {
  if (
    !Number.isInteger(amount) ||
    amount < MIN_DONATION ||
    amount > MAX_DONATION
  ) {
    return null;
  }


  const currentTier =
    getSupporterTier(amount);


  const nextTier =
    getNextSupporterTier(amount);


  if (!nextTier) {
    return {
      type: "achieved",
      icon: currentTier.icon,
      text:
        `👑 Okay ${currentTier.title}, top vibe unlocked! ` +
        `There's no higher title left to chase. ❤️‍🔥`,
    };
  }


  const difference =
    nextTier.amount - amount;


  return {
    type:
      amount >= currentTier.amount
        ? "next"
        : "next",

    icon:
      nextTier.icon,

    text:
      amount >= currentTier.amount
        ? `${currentTier.icon} ${currentTier.title} energy, confirmed. ₹${difference} more unlocks ${nextTier.title}.`
        : `${nextTier.icon} Just ₹${difference} away from ${nextTier.title} energy!`,
  };
}


/* =====================================================
   MAIN COMPONENT
   ===================================================== */

function DonationPage({
  onBack,
}: DonationPageProps) {

  const [name, setName] =
    useState("");

  const [amount, setAmount] =
    useState(100);

  const [customAmount, setCustomAmount] =
    useState("");

  const [nameAvailable, setNameAvailable] =
    useState<boolean | null>(null);

  const [loading, setLoading] =
    useState(false);


  /* =================================================
     RAZORPAY SCRIPT
     ================================================= */

  useEffect(() => {

    const existingScript =
      document.querySelector(
        'script[src="https://checkout.razorpay.com/v1/checkout.js"]'
      );


    if (existingScript) {
      return;
    }


    const script =
      document.createElement(
        "script"
      );


    script.src =
      "https://checkout.razorpay.com/v1/checkout.js";

    script.async = true;


    document.body.appendChild(
      script
    );


    return () => {

      if (
        document.body.contains(
          script
        )
      ) {
        document.body.removeChild(
          script
        );
      }

    };

  }, []);


  /* =================================================
     NAME AVAILABILITY
     ================================================= */

  useEffect(() => {

    if (!name.trim()) {

      setNameAvailable(
        null
      );

      return;
    }


    const timer =
      window.setTimeout(
        async () => {

          try {

            const response =
              await fetch(
                `${API_BASE_URL}/supporters/check-name?name=${encodeURIComponent(
                  name.trim()
                )}`
              );


            if (!response.ok) {

              setNameAvailable(
                null
              );

              return;
            }


            const data =
              await response.json();


            setNameAvailable(
              data.available === true
            );

          } catch {

            setNameAvailable(
              null
            );

          }

        },
        400
      );


    return () =>
      window.clearTimeout(
        timer
      );

  }, [name]);


  /* =================================================
     SELECTED AMOUNT
     ================================================= */

  const selectedAmount =
    useMemo(() => {

      if (
        customAmount.trim() !== ""
      ) {

        const value =
          Number(
            customAmount
          );


        if (
          !Number.isInteger(
            value
          )
        ) {
          return null;
        }


        return value;
      }


      return amount;

    }, [
      amount,
      customAmount,
    ]);


  /* =================================================
     CURRENT SUPPORTER MESSAGE
     ================================================= */

  const supporterMessage =
    selectedAmount !== null
      ? getSupporterMessage(
          selectedAmount
        )
      : null;


  /* =================================================
     CUSTOM AMOUNT
     ================================================= */

  function handleCustomAmountChange(
    value: string
  ) {

    const cleaned =
      value.replace(
        /\D/g,
        ""
      );


    setCustomAmount(
      cleaned
    );


    if (
      cleaned !== ""
    ) {

      const numericValue =
        Number(cleaned);


      if (
        Number.isInteger(
          numericValue
        )
      ) {

        setAmount(
          numericValue
        );

      }

    }

  }


  /* =================================================
     PRESET AMOUNT
     ================================================= */

  function selectPresetAmount(
    value: number
  ) {

    setAmount(
      value
    );

    setCustomAmount(
      ""
    );

  }


  /* =================================================
     DONATE
     ================================================= */

  async function donate() {

    if (!name.trim()) {

      alert(
        "Pick a Pujo name first ✨"
      );

      return;
    }


    if (
      nameAvailable !== true
    ) {

      alert(
        "That name's already taken — try another Pujo name 🎭"
      );

      return;
    }


    if (
      selectedAmount === null ||
      !Number.isInteger(
        selectedAmount
      )
    ) {

      alert(
        "Enter a valid whole-rupee vibe amount 💸"
      );

      return;
    }


    if (
      selectedAmount <
      MIN_DONATION
    ) {

      alert(
        "Minimum vibe amount is ₹1 🪔"
      );

      return;
    }


    if (
      selectedAmount >
      MAX_DONATION
    ) {

      alert(
        "Max vibe amount is ₹1,00,000 👑"
      );

      return;
    }


    setLoading(
      true
    );


    try {

      const response =
        await fetch(
          `${API_BASE_URL}/donations/create-order`,
          {
            method:
              "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify({
                display_name:
                  name.trim(),

                amount:
                  selectedAmount,
              }),
          }
        );


      if (!response.ok) {

        throw new Error(
          "Couldn't start the payment — please try again 🙏"
        );

      }


      const data =
        await response.json();


      if (!data.success) {

        throw new Error(
          data.message ||
            "Couldn't start the payment — please try again 🙏"
        );

      }


      const order =
        data.order;


      if (
        !window.Razorpay
      ) {

        throw new Error(
          "Payment portal is still loading — give it a sec and try again ⏳"
        );

      }


      const options = {

        key:
          order.key_id,

        amount:
          order.amount * 100,

        currency:
          "INR",

        name:
          "Kolkata Durga Puja Guide",

        description:
          "Support the Puja Guide",

        order_id:
          order.order_id,

        handler:
          async function (
            payment: any
          ) {

            try {

              const verificationResponse =
                await fetch(
                  `${API_BASE_URL}/donations/verify`,
                  {
                    method:
                      "POST",

                    headers: {
                      "Content-Type":
                        "application/json",
                    },

                    body:
                      JSON.stringify({
                        order_id:
                          payment.razorpay_order_id,

                        payment_id:
                          payment.razorpay_payment_id,

                        signature:
                          payment.razorpay_signature,
                      }),
                  }
                );


              const verification =
                await verificationResponse.json();


              if (
                verification.success
              ) {

                alert(
                  `You're officially Pujo Squad, ${name.trim()}! 🎉❤️`
                );


                window.location.href =
                  "/";

              } else {

                alert(
                  "Payment couldn't be verified. Please try again 🙏"
                );

              }

            } catch (
              verificationError
            ) {

              console.error(
                verificationError
              );


              alert(
                "Payment went through, but we couldn't confirm it yet. Please contact support 🙏"
              );

            }

          },

        prefill: {
          name:
            name.trim(),
        },

        theme: {
          color:
            "#7d2b20",
        },

      };


      const razorpay =
        new window.Razorpay(
          options
        );


      razorpay.open();

    } catch (error) {

      console.error(
        "Donation error:",
        error
      );


      alert(
        error instanceof Error
          ? error.message
          : "Something broke mid-vibe — please try again 🙏"
      );

    } finally {

      setLoading(
        false
      );

    }

  }


  /* =================================================
     RENDER
     ================================================= */

  return (
    <main className="app">

      <section className="screen-card donation-screen">


        {/* =========================================
            HEADER
            ========================================= */}

        <p className="festival-tag">
          🌺 SUPPORT THE PUJO GUIDE
        </p>


        <h1 className="screen-title">

          Keep the

          <span>
            Puja spirit alive
          </span>

        </h1>


        <p className="screen-subtitle">

          The guide is free for everyone.
          Support it only if you'd like to
          be part of the Pujo Squad.

        </p>


        {/* =========================================
            NAME
            ========================================= */}

        <div className="donation-field">

          <label>
            YOUR PUJO NAME
          </label>


          <div className="pujo-name-wrapper">

            <span>
              🌸
            </span>


            <input
              value={name}
              onChange={(event) =>
                setName(
                  event.target.value
                )
              }
              placeholder="Pick a unique name"
              maxLength={30}
            />

          </div>


          {nameAvailable === true && (
            <p className="name-success">
              ✓ Your name is available
            </p>
          )}


          {nameAvailable === false && (
            <p className="name-error">
              ⚠ That name is already taken.
            </p>
          )}

        </div>


        {/* =========================================
            AMOUNT
            ========================================= */}

        <div className="donation-field">

          <label>
            PICK YOUR PUJO VIBE
          </label>


          <div className="amount-grid">

            {PRESET_AMOUNTS.map(
              (value) => {

                const tier =
                  getSupporterTier(
                    value
                  );

                return (

                  <button
                    type="button"
                    key={value}
                    className={
                      customAmount === "" &&
                      amount === value
                        ? "amount-button active"
                        : "amount-button"
                    }
                    onClick={() =>
                      selectPresetAmount(
                        value
                      )
                    }
                  >

                    <span className="amount-button-icon">
                      {tier.icon}
                    </span>

                    <span className="amount-button-value">
                      ₹{value}
                    </span>

                  </button>

                );

              }
            )}

          </div>

        </div>


        {/* =========================================
            CUSTOM AMOUNT
            ========================================= */}

        <div className="donation-field">

          <label>
            OR WRITE YOUR OWN VIBE
          </label>


          <div className="custom-amount-wrapper">

            <span>
              ₹
            </span>


            <input
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              value={
                customAmount
              }
              onChange={(event) =>
                handleCustomAmountChange(
                  event.target.value
                )
              }
              placeholder="Any amount from ₹1"
              maxLength={6}
            />

          </div>


          <p className="custom-amount-help">

            Every rupee counts. Thanks for supporting the guide! ❤️

          </p>


          {supporterMessage && (
            <div
              className={`supporter-tier-message ${
                supporterMessage.type
              }`}
            >

              <span>
                {supporterMessage.icon}
              </span>

              <p>
                {supporterMessage.text}
              </p>

            </div>
          )}


          {customAmount !== "" &&
            selectedAmount === null && (
              <p className="name-error">
                ⚠ Please enter a valid
                whole-rupee amount.
              </p>
            )}


          {selectedAmount !== null &&
            selectedAmount < 1 && (
              <p className="name-error">
                ⚠ Minimum donation is ₹1.
              </p>
            )}


          {selectedAmount !== null &&
            selectedAmount > 100000 && (
              <p className="name-error">
                ⚠ Maximum donation is
                ₹1,00,000.
              </p>
            )}

        </div>


        {/* =========================================
            CURRENT VIBE
            ========================================= */}

        {selectedAmount !== null &&
          selectedAmount >= 1 &&
          selectedAmount <=
            MAX_DONATION && (

          <div className="current-pujo-vibe">

            <span>
              {
                getSupporterTier(
                  selectedAmount
                ).icon
              }
            </span>


            <div>

              <p>
                YOUR CURRENT PUJO VIBE
              </p>


              <strong>
                {
                  getSupporterTier(
                    selectedAmount
                  ).title
                }
              </strong>

            </div>


            <b>
              ₹
              {selectedAmount.toLocaleString(
                "en-IN"
              )}
            </b>

          </div>
        )}


        {/* =========================================
            PAYMENT BUTTON
            ========================================= */}

        <button
          className="start-button"
          disabled={
            loading ||
            nameAvailable !== true ||
            selectedAmount === null ||
            selectedAmount < 1 ||
            selectedAmount > 100000
          }
          onClick={donate}
        >

          {loading
            ? "Opening payment portal... ✨"
            : `🎉 Join with ₹${(
                selectedAmount ?? 0
              ).toLocaleString(
                "en-IN"
              )}`}

        </button>


        {/* =========================================
            PUJO RANK BOARD
            ========================================= */}

        <div className="pujo-rank-board">

          <div className="pujo-rank-header">

            <div className="pujo-rank-heading-left">

              <span className="pujo-rank-heading-icon">
                🪩
              </span>


              <div>

                <p>
                  PUJO RANK BOARD
                </p>


                <h2>
                  Unlock your Pujo vibe
                </h2>

              </div>

            </div>


            <span className="rank-board-sparkle">
              ✨
            </span>

          </div>


          <div className="pujo-rank-progress">

            <div className="pujo-rank-progress-track">

              <div
                className="pujo-rank-progress-fill"
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(
                      0,
                      ((selectedAmount ?? 0) /
                        SUPPORTER_TIERS[0]
                          .amount) *
                        100
                    )
                  )}%`,
                }}
              />

            </div>

            <div className="pujo-rank-progress-labels">

              <span>₹0</span>

              <span>👑 ₹{SUPPORTER_TIERS[0].amount}+</span>

            </div>

          </div>


          <div className="pujo-rank-list">

            {SUPPORTER_TIERS.map(
              (
                tier
              ) => {

                const active =
                  selectedAmount !== null &&
                  selectedAmount >=
                    tier.amount;


                const nextTier =
                  selectedAmount !== null
                    ? getNextSupporterTier(
                        selectedAmount
                      )
                    : undefined;


                const isNext =
                  nextTier?.amount ===
                  tier.amount;


                return (
                  <div
                    className={`pujo-rank-item ${
                      active
                        ? "unlocked"
                        : ""
                    } ${
                      isNext
                        ? "next-rank"
                        : ""
                    }`}
                    key={
                      tier.amount
                    }
                  >

                    <span className="rank-icon">
                      {tier.icon}
                    </span>


                    <div className="rank-info">

                      <strong>
                        {tier.title}
                      </strong>

                      <span>
                        {tier.amount === 1
                          ? "₹1+"
                          : `₹${tier.amount}+`}
                      </span>

                    </div>


                    <span
                      className={`rank-state ${
                        active
                          ? "state-unlocked"
                          : isNext
                          ? "state-next"
                          : "state-locked"
                      }`}
                    >

                      {active
                        ? "✓ Unlocked"
                        : isNext
                        ? "🔥 Next"
                        : "🔒"}

                    </span>

                  </div>
                );

              }
            )}

          </div>


          <p className="rank-board-note">

            Everyone who supports the guide gets
            a vibe. Go bigger to unlock spicier
            titles. 🌺✨

          </p>

        </div>


        {/* =========================================
            BACK
            ========================================= */}

        <button
          className="back-button"
          onClick={
            onBack
          }
        >
          ← Back
        </button>

      </section>

    </main>
  );
}


export default DonationPage;